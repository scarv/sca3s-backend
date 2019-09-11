# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend as be
from sca3s import spec    as spec

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import h5py, numpy, os, random

class Block( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

  def prepare( self ) : 
    if ( self.job.board.driver_id != 'block' ) :
      raise Exception()

    self.kernel_sizeof_k = int( self.job.board.interact( '?reg k' ), 16 )
    self.kernel_sizeof_r = int( self.job.board.interact( '?reg r' ), 16 )
    self.kernel_sizeof_m = int( self.job.board.interact( '?reg m' ), 16 )
    self.kernel_sizeof_c = int( self.job.board.interact( '?reg c' ), 16 )

    self.job.log.info( '?reg k -> kernel sizeof( k ) = %s', self.kernel_sizeof_k )
    self.job.log.info( '?reg r -> kernel sizeof( r ) = %s', self.kernel_sizeof_r )
    self.job.log.info( '?reg m -> kernel sizeof( m ) = %s', self.kernel_sizeof_m )
    self.job.log.info( '?reg c -> kernel sizeof( c ) = %s', self.kernel_sizeof_c )

  def execute( self ) :
    trace_spec    = self.job.conf.get( 'trace-spec' )

    trace_content =       trace_spec.get( 'content' )
    trace_count   =  int( trace_spec.get( 'count'   ) )

    fd = h5py.File( os.path.join( self.job.path, 'acquire.hdf5' ), 'a' )

    fd.attrs.create( 'driver_version',    self.job.board.driver_version,    dtype = h5py.special_dtype( vlen = str ) )
    fd.attrs.create( 'driver_id',         self.job.board.driver_id,         dtype = h5py.special_dtype( vlen = str ) )
    fd.attrs.create( 'kernel_id',         self.job.board.kernel_id,         dtype = h5py.special_dtype( vlen = str ) )
    
    fd.attrs.create( 'kernel_sizeof_k',   self.kernel_sizeof_k,             dtype = '<u8'                            )
    fd.attrs.create( 'kernel_sizeof_r',   self.kernel_sizeof_r,             dtype = '<u8'                            )
    fd.attrs.create( 'kernel_sizeof_m',   self.kernel_sizeof_m,             dtype = '<u8'                            )
    fd.attrs.create( 'kernel_sizeof_c',   self.kernel_sizeof_c,             dtype = '<u8'                            )
    
    fd.attrs.create( 'signal_interval',   self.job.scope.signal_interval,   dtype = '<f8'                            )
    fd.attrs.create( 'signal_duration',   self.job.scope.signal_duration,   dtype = '<f8'                            )
    
    fd.attrs.create( 'signal_resolution', self.job.scope.signal_resolution, dtype = '<u8'                            )
    fd.attrs.create( 'signal_type',       self.job.scope.signal_type,       dtype = h5py.special_dtype( vlen = str ) )
    fd.attrs.create( 'signal_length',     self.job.scope.signal_length,     dtype = '<u8'                            )

    if ( 'trace/trigger'  in trace_content ) :
      fd.create_dataset( 'trace/trigger', ( trace_count, self.job.scope.signal_length ), dtype = self.job.scope.signal_type )
    if ( 'trace/signal'   in trace_content ) :
      fd.create_dataset( 'trace/signal',  ( trace_count, self.job.scope.signal_length ), dtype = self.job.scope.signal_type )
    if (  'crop/trigger'  in trace_content ) :
      fd.create_dataset(  'crop/trigger', ( trace_count,                              ), dtype = h5py.special_dtype( ref = h5py.RegionReference ) )
    if (  'crop/signal'   in trace_content ) :
      fd.create_dataset(  'crop/signal',  ( trace_count,                              ), dtype = h5py.special_dtype( ref = h5py.RegionReference ) )

    if (  'perf/cycle'    in trace_content ) :
      fd.create_dataset(  'perf/cycle',   ( trace_count,                              ), dtype = '<u8' )
    if (  'perf/duration' in trace_content ) :
      fd.create_dataset(  'perf/time',    ( trace_count,                              ), dtype = '<f8' )

    if ( 'k'              in trace_content ) :
      fd.create_dataset( 'k',             ( trace_count, self.kernel_sizeof_k         ), dtype =   'B' )
    if ( 'r'              in trace_content ) :
      fd.create_dataset( 'r',             ( trace_count, self.kernel_sizeof_k         ), dtype =   'B' )
    if ( 'm'              in trace_content ) :
      fd.create_dataset( 'm',             ( trace_count, self.kernel_sizeof_k         ), dtype =   'B' )
    if ( 'c'              in trace_content ) :
      fd.create_dataset( 'c',             ( trace_count, self.kernel_sizeof_k         ), dtype =   'B' )

    k = bytes( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_k ) ] )

    for i in range( trace_count ) :
      self.job.log.indent_inc( message = 'started  acquiring trace {0:>{width}d} of {1:d}'.format( i, trace_count, width = len( str( trace_count ) ) ) )

      trace            = self.acquire( k = k )

      trigger_edge_lo  = be.share.util.measure( be.share.util.MEASURE_MODE_TRIGGER_POS, trace[ 'trace/trigger' ], self.job.scope.channel_trigger_threshold )
      trigger_edge_hi  = be.share.util.measure( be.share.util.MEASURE_MODE_TRIGGER_NEG, trace[ 'trace/trigger' ], self.job.scope.channel_trigger_threshold )
      
      trigger_cycle    = trace[ 'perf/cycle' ]
      trigger_duration = float( trigger_edge_hi - trigger_edge_lo ) * self.job.scope.signal_interval

      self.job.log.info( 'trigger cycle    = {0:d}'.format( trigger_cycle    ) )
      self.job.log.info( 'trigger duration = {0:g}'.format( trigger_duration ) )
      self.job.log.info( '        +ve edge @ {0:d}'.format( trigger_edge_lo  ) )
      self.job.log.info( '        -ve edge @ {0:d}'.format( trigger_edge_hi  ) )

      if ( 'trace/trigger' in trace_content ) :
        fd[ 'trace/trigger'  ][ i ] = trace[ 'trace/trigger' ]
      if ( 'trace/signal'  in trace_content ) :
        fd[ 'trace/signal'   ][ i ] = trace[ 'trace/signal'  ]

      if (  'crop/trigger' in trace_content ) :
        fd[  'crop/trigger'  ][ i ] = fd[ 'trace/trigger' ].regionref[ i, trigger_edge_lo : trigger_edge_hi ]
      if (  'crop/signal'  in trace_content ) :
        fd[  'crop/signal'   ][ i ] = fd[ 'trace/signal'  ].regionref[ i, trigger_edge_lo : trigger_edge_hi ]

      if (  'perf/cycle'          in trace_content ) :
        fd[  'perf/cycle'    ][ i ] = trigger_cycle
      if (  'perf/duration'          in trace_content ) :
        fd[  'perf/duration' ][ i ] = trigger_duration

      if ( 'k'            in trace_content ) :
        fd[ 'k'              ][ i ] = numpy.frombuffer( trace[ 'k' ], dtype = numpy.uint8 )
      if ( 'r'            in trace_content ) :
        fd[ 'r'              ][ i ] = numpy.frombuffer( trace[ 'r' ], dtype = numpy.uint8 )
      if ( 'm'            in trace_content ) :
        fd[ 'm'              ][ i ] = numpy.frombuffer( trace[ 'm' ], dtype = numpy.uint8 )
      if ( 'c'            in trace_content ) :
        fd[ 'c'              ][ i ] = numpy.frombuffer( trace[ 'c' ], dtype = numpy.uint8 )

      self.job.log.indent_dec( message = 'finished acquiring trace {0:>{width}d} of {1:d}'.format( i, trace_count, width = len( str( trace_count ) ) ) )

    fd.close()

    self.job.run( [ 'gzip', '--quiet', os.path.join( self.job.path, 'acquire.hdf5' ) ] )
