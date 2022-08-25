# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import hybrid as hybrid

from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import abc, h5py, numpy, os


CONF_DERIVE_RESOLUTION =    0
CONF_DERIVE_DURATION   =    1
CONF_DERIVE_INTERVAL   =    2

CONF_SELECT_INIT       =    0
CONF_SELECT_FINI       =    1

CONF_RESOLUTION_MIN    =    0
CONF_RESOLUTION_MAX    = 1024

ACQUIRE_MODE_PRIME     = 0x01
ACQUIRE_MODE_FETCH     = 0x02

class ScopeAbs( abc.ABC ) :
  def __init__( self, job ) :
    self.job                       = job

    self.scope_id                  = self.job.conf.get( 'scope_id'   )
    self.scope_spec                = self.job.conf.get( 'scope_spec' )
    self.scope_mode                = self.job.conf.get( 'scope_mode' )
    self.scope_path                = self.job.conf.get( 'scope_path' )

    self.scope_unit                = None

    self.channel_trigger_range     = None
    self.channel_trigger_threshold = None
    self.channel_acquire_range     = None
    self.channel_acquire_threshold = None

    self.signal_resolution         = None
    self.signal_dtype              = None

    self.signal_interval           = None
    self.signal_duration           = None
    self.signal_samples            = None

  def __str__( self ) :
    return self.scope_id

  def calibrate( self, dtype = None, resolution = None ) :
    trace_spec             = self.job.conf.get( 'trace_spec' )

    trace_calibrate_trials = int( trace_spec.get( 'calibrate_trials' ) )
    trace_calibrate_margin = int( trace_spec.get( 'calibrate_margin' ) )

    if ( not os.path.isdir( os.path.join( self.job.path, 'calibrate' ) ) ) :
      os.mkdir( os.path.join( self.job.path, 'calibrate' ) )

    def step( fd, n ) :
      #fd.create_dataset( 'trace/trigger', ( n, self.signal_samples ), self.signal_dtype )
      #fd.create_dataset( 'trace/content', ( n, self.signal_samples ), self.signal_dtype )

      ls = list()
 
      for i in range( n ) :
        traces   = self.job.driver.acquire() 

        edge_pos = traces[  0 ][ 'edge/pos' ]
        edge_neg = traces[ -1 ][ 'edge/neg' ]

        #fd[ 'trace/trigger' ][ i ] = sca3s_be.share.util.resize( trace[ 'trace/trigger' ], self.signal_samples, dtype = self.signal_dtype )
        #fd[ 'trace/content' ][ i ] = sca3s_be.share.util.resize( trace[ 'trace/content' ], self.signal_samples, dtype = self.signal_dtype )

        ls.append( ( edge_neg - edge_pos ) * self.job.scope.signal_interval )

      return ls

    # step #0: default

    self.job.log.indent_inc( message = 'auto-calibration step #0: default'        )

    t  = self.conf_select( scope.CONF_SELECT_INIT, dtype = dtype, resolution = resolution )
    self.job.log.info( 't_conf = %s', str( t ) )

    self.job.log.indent_dec()

    # step #1: 1 * large trial(s)

    self.job.log.indent_inc( message = 'auto-calibration step #1: large trial(s)' )

    with h5py.File( os.path.join( self.job.path, 'calibrate', 'calibrate-step_1.hdf5' ), 'a' ) as fd :
      ls = step( fd, 1                      ) ; l  = max( ls ) ; l = ( 2 * l ) 

    self.job.log.info( 'ls = %s -> l = %s', str( ls ), str( l ) )
    t  = self.conf_select( scope.CONF_SELECT_FINI, dtype = t[ 'dtype' ], resolution = t[ 'resolution' ], interval = t[ 'interval' ], duration = l )
    self.job.log.info( 't_conf = %s', str( t ) )

    self.job.log.indent_dec()

    # step #2: n * small trial(s) + margin

    self.job.log.indent_inc( message = 'auto-calibration step #2: small trial(s)' )

    with h5py.File( os.path.join( self.job.path, 'calibrate', 'calibrate-step_2.hdf5' ), 'a' ) as fd :
      ls = step( fd, trace_calibrate_trials ) ; l  = max( ls ) ; l = ( 1 * l ) + ( ( trace_calibrate_margin / 100 ) * l )

    self.job.log.info( 'ls = %s -> l = %s', str( ls ), str( l ) )
    t  = self.conf_select( scope.CONF_SELECT_FINI, dtype = t[ 'dtype' ], resolution = t[ 'resolution' ], interval = t[ 'interval' ], duration = l )
    self.job.log.info( 't_conf = %s', str( t ) )

    self.job.log.indent_dec()

    # step #3: 1 * final trial(s)

    self.job.log.indent_inc( message = 'auto-calibration step #3: final trial(s)' )

    with h5py.File( os.path.join( self.job.path, 'calibrate', 'calibrate-step_3.hdf5' ), 'a' ) as fd :
      ls = step( fd, 1                      ) ; l  = max( ls ) ; l = ( 1 * l )

    self.job.log.indent_dec()

    return l

  def hdf5_add_attr( self, trace_content, fd              ) :
    fd.attrs.create( 'scope/signal_dtype',      str( self.signal_dtype      ), dtype = h5py.string_dtype() )
    fd.attrs.create( 'scope/signal_resolution',    ( self.signal_resolution ), dtype = '<u8'               )

    fd.attrs.create( 'scope/signal_interval',      ( self.signal_interval   ), dtype = '<f8'               )
    fd.attrs.create( 'scope/signal_duration',      ( self.signal_duration   ), dtype = '<f8'               )

    fd.attrs.create( 'scope/signal_samples',       ( self.signal_samples    ), dtype = '<u8'               )

  def hdf5_add_data( self, trace_content, fd, n           ) :
    if ( 'trace/trigger' in trace_content ) :
      fd.create_dataset( 'trace/trigger',  ( n, self.signal_samples ), dtype =    self.signal_dtype )
    if ( 'trace/signal'  in trace_content ) :
      fd.create_dataset( 'trace/signal',   ( n, self.signal_samples ), dtype =    self.signal_dtype )
    if (  'crop/trigger' in trace_content ) :
      fd.create_dataset(  'crop/trigger',  ( n,                     ), dtype = h5py.regionref_dtype )
    if (  'crop/signal'  in trace_content ) :
      fd.create_dataset(  'crop/signal',   ( n,                     ), dtype = h5py.regionref_dtype )

  def hdf5_set_data( self, trace_content, fd, n, i, trace ) :
    if ( 'trace/trigger' in trace ) :
      trace[ 'trace/trigger' ] = sca3s_be.share.util.resize( trace[ 'trace/trigger' ], self.signal_samples, dtype = self.signal_dtype )
    if ( 'trace/signal'  in trace ) :
      trace[ 'trace/content' ] = sca3s_be.share.util.resize( trace[ 'trace/content' ], self.signal_samples, dtype = self.signal_dtype )
    if ( 'edge/pos'      in trace ) :
      trace[ 'edge/pos'      ] = min( trace[ 'edge/pos' ], self.signal_samples - 1 )
    if ( 'edge/neg'      in trace ) :
      trace[ 'edge/neg'      ] = min( trace[ 'edge/neg' ], self.signal_samples - 1 )

    if ( 'trace/trigger' in trace_content ) :
      fd[ 'trace/trigger' ][ i ] = trace[ 'trace/trigger' ]
    if ( 'trace/signal'  in trace_content ) :
      fd[ 'trace/signal'  ][ i ] = trace[ 'trace/content' ]
    if (  'crop/trigger' in trace_content ) :
      fd[  'crop/trigger' ][ i ] =    fd[ 'trace/trigger' ].regionref[ i, trace[ 'edge/pos' ] : trace[ 'edge/neg' ] ]
    if (  'crop/signal'  in trace_content ) :
      fd[  'crop/signal'  ][ i ] =    fd[ 'trace/signal'  ].regionref[ i, trace[ 'edge/pos' ] : trace[ 'edge/neg' ] ]

  @abc.abstractmethod
  def conf_derive( self, mode, dtype = None, resolution = None, interval = None, duration = None ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def conf_select( self, mode, dtype = None, resolution = None, interval = None, duration = None ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def acquire( self, mode = scope.ACQUIRE_MODE_PRIME | scope.ACQUIRE_MODE_FETCH ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def    open( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def   close( self ) :
    raise NotImplementedError()
