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
from sca3s.backend.acquire import kernel as kernel

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import abc, h5py, numpy, os

CALIBRATE_MODE_DEFAULT   =    0
CALIBRATE_MODE_DURATION  =    1
CALIBRATE_MODE_INTERVAL  =    2
CALIBRATE_MODE_FREQUENCY =    3
CALIBRATE_MODE_AUTO      =    4

CALIBRATE_STEP_0         =    0
CALIBRATE_STEP_1         =    1
CALIBRATE_STEP_2         =    2
CALIBRATE_STEP_3         =    3

RESOLUTION_MIN           =    0
RESOLUTION_MAX           = 1024

ACQUIRE_MODE_PRIME       = 0x01
ACQUIRE_MODE_FETCH       = 0x02

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

  def _autocalibrate( self, resolution = 8, dtype = '<f8' ) :
    trace_spec             = self.job.conf.get( 'trace_spec' )

    trace_calibrate_trials = int( trace_spec.get( 'calibrate_trials' ) )
    trace_calibrate_margin = int( trace_spec.get( 'calibrate_margin' ) )

    if ( not os.path.isdir( os.path.join( self.job.path, 'calibrate' ) ) ) :
      os.mkdir( os.path.join( self.job.path, 'calibrate' ) )

    def step( fd, n ) :
      fd.create_dataset( 'trace/trigger', ( n, self.signal_samples ), self.signal_dtype )
      fd.create_dataset( 'trace/signal',  ( n, self.signal_samples ), self.signal_dtype )

      ls = list()
 
      for i in range( n ) :
        trace = self.job.driver.acquire()

        fd[ 'trace/trigger' ][ i ] = sca3s_be.share.util.resize( trace[ 'trace/trigger' ], self.signal_samples, dtype = self.signal_dtype )
        fd[ 'trace/signal'  ][ i ] = sca3s_be.share.util.resize( trace[ 'trace/signal'  ], self.signal_samples, dtype = self.signal_dtype )

        ls.append( sca3s_be.share.util.measure( sca3s_be.share.util.MEASURE_MODE_DURATION, trace[ 'trace/trigger' ], self.job.scope.channel_trigger_threshold ) * self.job.scope.signal_interval )

      return ls

    # step #0: default

    self.job.log.indent_inc( message = 'auto-calibration step #0: default'        )

    t  = self.calibrate( mode = scope.CALIBRATE_MODE_DEFAULT,             resolution = resolution, dtype = dtype )
    self.job.log.info( 't_conf = %s', str( t ) )

    self.job.log.indent_dec()

    # step #1: 1 * large trial(s)

    self.job.log.indent_inc( message = 'auto-calibration step #1: large trial(s)' )

    with h5py.File( os.path.join( self.job.path, 'calibrate', 'calibrate-step_1.hdf5' ), 'a' ) as fd :
      ls = step( fd, 1                      ) ; l  = max( ls ) ; l = ( 2 * l ) 

    self.job.log.info( 'ls = %s -> l = %s', str( ls ), str( l ) )
    t  = self.calibrate( mode = scope.CALIBRATE_MODE_DURATION, value = l, resolution = resolution, dtype = dtype )
    self.job.log.info( 't_conf = %s', str( t ) )

    self.job.log.indent_dec()

    # step #2: n * small trial(s) + margin

    self.job.log.indent_inc( message = 'auto-calibration step #2: small trial(s)' )

    with h5py.File( os.path.join( self.job.path, 'calibrate', 'calibrate-step_2.hdf5' ), 'a' ) as fd :
      ls = step( fd, trace_calibrate_trials ) ; l  = max( ls ) ; l = ( 1 * l ) + ( ( trace_calibrate_margin / 100 ) * l )

    self.job.log.info( 'ls = %s -> l = %s', str( ls ), str( l ) )
    t = self.calibrate( mode = scope.CALIBRATE_MODE_DURATION, value = l, resolution = resolution, dtype = dtype )
    self.job.log.info( 't_conf = %s', str( t ) )

    self.job.log.indent_dec()

    # step #3: 1 * final trial(s)

    self.job.log.indent_inc( message = 'auto-calibration step #3: final trial(s)' )

    with h5py.File( os.path.join( self.job.path, 'calibrate', 'calibrate-step_3.hdf5' ), 'a' ) as fd :
      ls = step( fd, 1                      ) ; l  = max( ls ) ; l = ( 1 * l )

    self.job.log.indent_dec()

    return t

  def hdf5_add_attr( self, trace_content, fd              ) :
    spec = [ ( 'signal_resolution',    ( self.signal_resolution ), '<u8'                            ),
             ( 'signal_dtype',      str( self.signal_dtype      ), h5py.special_dtype( vlen = str ) ),

             ( 'signal_interval',      ( self.signal_interval   ), '<f8'                            ),
             ( 'signal_duration',      ( self.signal_duration   ), '<f8'                            ),  
             ( 'signal_samples',       ( self.signal_samples    ), '<u8'                            ) ]

    sca3s_be.share.util.hdf5_add_attr( spec, trace_content, fd              )

  def hdf5_add_data( self, trace_content, fd, n           ) :
    spec = [ ( 'trace/trigger',  ( n, self.signal_samples ),   self.signal_dtype ),
             ( 'trace/signal',   ( n, self.signal_samples ),   self.signal_dtype ),
   
             (  'crop/trigger',  ( n,                     ), h5py.regionref_dtype ),
             (  'crop/signal',   ( n,                     ), h5py.regionref_dtype ) ]

    sca3s_be.share.util.hdf5_add_data( spec, trace_content, fd, n           )

  def hdf5_set_data( self, trace_content, fd, n, i, trace ) :
    spec = [ ( 'trace/trigger',  lambda trace : trace[ 'trace/trigger' ]                                                           ),
             ( 'trace/signal',   lambda trace : trace[ 'trace/signal'  ]                                                           ),

             (  'crop/trigger',  lambda trace :    fd[ 'trace/trigger' ].regionref[ i, trace[ 'edge/pos' ] : trace[ 'edge/neg' ] ] ),
             (  'crop/signal',   lambda trace :    fd[ 'trace/signal'  ].regionref[ i, trace[ 'edge/pos' ] : trace[ 'edge/neg' ] ] ) ]

    if ( 'trace/trigger' in trace ) :
      trace[ 'trace/trigger' ] = sca3s_be.share.util.resize( trace[ 'trace/trigger' ], self.signal_samples, dtype = self.signal_dtype )
    if ( 'trace/signal'  in trace ) :
      trace[ 'trace/signal'  ] = sca3s_be.share.util.resize( trace[ 'trace/signal'  ], self.signal_samples, dtype = self.signal_dtype )
    if ( 'edge/pos'      in trace ) :
      trace[ 'edge/pos'      ] = min( trace[ 'edge/pos' ], self.signal_samples - 1 )
    if ( 'edge/neg'      in trace ) :
      trace[ 'edge/neg'      ] = min( trace[ 'edge/neg' ], self.signal_samples - 1 )

    sca3s_be.share.util.hdf5_set_data( spec, trace_content, fd, n, i, trace )

  @abc.abstractmethod
  def calibrate( self, mode = scope.CALIBRATE_MODE_DEFAULT, value = None, resolution = 8, dtype = '<f8' ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def   acquire( self, mode = scope.ACQUIRE_MODE_PRIME | scope.ACQUIRE_MODE_FETCH ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def      open( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def     close( self ) :
    raise NotImplementedError()
