# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import binascii, h5py, importlib, numpy, os

class DriverImp( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.trace_spec    = self.job.conf.get( 'trace_spec' )

    self.trace_content =       self.trace_spec.get( 'content' )
    self.trace_count   =  int( self.trace_spec.get( 'count'   ) )

    self.kernel        = None

    self.policy_id     = self.driver_spec.get( 'policy_id'   )
    self.policy_spec   = self.driver_spec.get( 'policy_spec' )

  def _acquire_log_inc( self, i, n, message = None ) :
    width = len( str( n ) ) ; message = '' if ( message == None ) else ( ' : ' + message )
    self.job.log.indent_inc( message = 'started  acquiring trace {0:>{width}d} of {1:d} {message:s}'.format( i, n, width = width, message = message  ) )

  def _acquire_log_dec( self, i, n, message = None ) :
    width = len( str( n ) ) ; message = '' if ( message == None ) else ( ' : ' + message )
    self.job.log.indent_dec( message = 'finished acquiring trace {0:>{width}d} of {1:d} {message:s}'.format( i, n, width = width, message = message  ) )

  def _acquire_enc( self, r = None, k = None, m = None ) :
    if ( r == None ) :
      r = self.kernel.value( '{$*|r|}' )
    if ( k == None ) :
      k = self.kernel.value( '{$*|k|}' )
    if ( m == None ) :
      m = self.kernel.value( '{$*|m|}' )

    self.job.board.interact( '>data r %s' % sca3s_be.share.util.str2octetstr( r ).upper() )
    self.job.board.interact( '>data k %s' % sca3s_be.share.util.str2octetstr( k ).upper() )
    self.job.board.interact( '>data m %s' % sca3s_be.share.util.str2octetstr( m ).upper() )
  
    _                   = self.job.scope.acquire( mode = scope.ACQUIRE_MODE_PRIME )

    self.job.board.interact( '!kernel_prologue' )
    self.job.board.interact( '!kernel'          )
    self.job.board.interact( '!kernel_epilogue' )
  
    ( trigger, signal ) = self.job.scope.acquire( mode = scope.ACQUIRE_MODE_FETCH )
  
    c = sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data c' ) )

    sca3s_be.share.sys.log.debug( 'acquire : r = %s', binascii.b2a_hex( r ) )
    sca3s_be.share.sys.log.debug( 'acquire : k = %s', binascii.b2a_hex( k ) )
    sca3s_be.share.sys.log.debug( 'acquire : m = %s', binascii.b2a_hex( m ) )
    sca3s_be.share.sys.log.debug( 'acquire : c = %s', binascii.b2a_hex( c ) )

    if ( self.driver_spec.get( 'verify' ) ) :
      t = self.kernel.enc( k, m )

      if ( ( t != None ) and ( t != c ) ) :
        raise Exception( 'failed I/O verification during acquisition => enc( k, m ) != c' )  

    cycle_enc = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data tsc' ) ), 2 ** 8 )
    self.job.board.interact( '!nop' )
    cycle_nop = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data tsc' ) ), 2 ** 8 )

    ( edge_hi, edge_lo, duration ) = self._measure( trigger )

    return { 'trace/trigger' : trigger, 'trace/signal' : signal, 'edge/hi' : edge_hi, 'edge/lo' : edge_lo, 'perf/cycle' : cycle_enc - cycle_nop, 'perf/duration' : duration, 'r' : r, 'k' : k, 'm' : m, 'c' : c }

  def _acquire_dec( self, r = None, k = None, c = None ) :
    if ( r == None ) :
      r = self.kernel.value( '{$*|r|}' )
    if ( k == None ) :
      k = self.kernel.value( '{$*|k|}' )
    if ( c == None ) :
      c = self.kernel.value( '{$*|c|}' )

    self.job.board.interact( '>data r %s' % sca3s_be.share.util.str2octetstr( r ).upper() )
    self.job.board.interact( '>data k %s' % sca3s_be.share.util.str2octetstr( k ).upper() )
    self.job.board.interact( '>data c %s' % sca3s_be.share.util.str2octetstr( c ).upper() )
  
    _                   = self.job.scope.acquire( mode = scope.ACQUIRE_MODE_PRIME )
  
    self.job.board.interact( '!kernel_prologue' )
    self.job.board.interact( '!kernel'          )
    self.job.board.interact( '!kernel_epilogue' )
  
    ( trigger, signal ) = self.job.scope.acquire( mode = scope.ACQUIRE_MODE_FETCH )
  
    m = sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data m' ) )

    sca3s_be.share.sys.log.debug( 'acquire : r = %s', binascii.b2a_hex( r ) )
    sca3s_be.share.sys.log.debug( 'acquire : k = %s', binascii.b2a_hex( k ) )
    sca3s_be.share.sys.log.debug( 'acquire : c = %s', binascii.b2a_hex( c ) )
    sca3s_be.share.sys.log.debug( 'acquire : m = %s', binascii.b2a_hex( m ) )

    if ( self.driver_spec.get( 'verify' ) ) :
      t = self.kernel.dec( k, c )

      if ( ( t != None ) and ( t != m ) ) :
        raise Exception( 'failed I/O verification during acquisition => dec( k, c ) != m' )  

    cycle_dec = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data tsc' ) ), 2 ** 8 )
    self.job.board.interact( '!nop' )
    cycle_nop = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data tsc' ) ), 2 ** 8 )

    ( edge_hi, edge_lo, duration ) = self._measure( trigger )

    return { 'trace/trigger' : trigger, 'trace/signal' : signal, 'edge/hi' : edge_hi, 'edge/lo' : edge_lo, 'perf/cycle' : cycle_dec - cycle_nop, 'perf/duration' : duration, 'r' : r, 'k' : k, 'm' : m, 'c' : c }    

  def _hdf5_add_attr( self, fd ) :
    T = [ ( 'driver_version',    self.job.board.driver_version,    h5py.special_dtype( vlen = str ) ),
          ( 'driver_id',         self.job.board.driver_id,         h5py.special_dtype( vlen = str ) ),
          ( 'kernel_id',         self.job.board.kernel_id,         h5py.special_dtype( vlen = str ) ),

          ( 'kernel_sizeof_k',   self.kernel.sizeof_k,             '<u8'                            ),
          ( 'kernel_sizeof_r',   self.kernel.sizeof_r,             '<u8'                            ),
          ( 'kernel_sizeof_m',   self.kernel.sizeof_m,             '<u8'                            ),
          ( 'kernel_sizeof_c',   self.kernel.sizeof_c,             '<u8'                            ),

          ( 'signal_interval',   self.job.scope.signal_interval,   '<f8'                            ),
          ( 'signal_duration',   self.job.scope.signal_duration,   '<f8'                            ),
    
          ( 'signal_resolution', self.job.scope.signal_resolution, '<u8'                            ),
          ( 'signal_type',       self.job.scope.signal_type,       h5py.special_dtype( vlen = str ) ),
          ( 'signal_length',     self.job.scope.signal_length,     '<u8'                            ) ]
    
    for ( k, v, t ) in T :
      fd.attrs.create( k, v, dtype = t )

  def _hdf5_add_data( self, fd, n ) :
    T = [ ( 'trace/trigger',  ( n, self.job.scope.signal_length ), self.job.scope.signal_type                       ),
          ( 'trace/signal',   ( n, self.job.scope.signal_length ), self.job.scope.signal_type                       ),
   
          (  'crop/trigger',  ( n,                              ), h5py.special_dtype( ref = h5py.RegionReference ) ),
          (  'crop/signal',   ( n,                              ), h5py.special_dtype( ref = h5py.RegionReference ) ),
   
          (  'perf/cycle',    ( n,                              ), '<u8'                                            ),
          (  'perf/duration', ( n,                              ), '<f8'                                            ),
   
          ( 'r',              ( n, self.kernel.sizeof_k         ),   'B'                                            ),
          ( 'k',              ( n, self.kernel.sizeof_k         ),   'B'                                            ),
          ( 'm',              ( n, self.kernel.sizeof_k         ),   'B'                                            ),
          ( 'c',              ( n, self.kernel.sizeof_k         ),   'B'                                            ) ]

    for ( k, v, t ) in T :
      if ( k in self.trace_content ) :
        fd.create_dataset( k, v, t )
 
  def _hdf5_set_data( self, fd, trace, i ) :
    T = [ ( 'trace/trigger',  lambda trace : trace[ 'trace/trigger'  ]                                                         ),
          ( 'trace/signal',   lambda trace : trace[ 'trace/signal'   ]                                                         ),

          (  'crop/trigger',  lambda trace :    fd[ 'trace/trigger'  ].regionref[ i, trace[ 'edge/lo' ] : trace[ 'edge/hi' ] ] ),
          (  'crop/signal',   lambda trace :    fd[ 'trace/signal'   ].regionref[ i, trace[ 'edge/lo' ] : trace[ 'edge/hi' ] ] ),

          (  'perf/cycle',    lambda trace : trace[  'perf/cycle'    ]                                                         ),
          (  'perf/duration', lambda trace : trace[  'perf/duration' ]                                                         ),

          ( 'r',              lambda trace : numpy.frombuffer( trace[ 'r' ], dtype = numpy.uint8 )                             ),
          ( 'k',              lambda trace : numpy.frombuffer( trace[ 'k' ], dtype = numpy.uint8 )                             ),
          ( 'm',              lambda trace : numpy.frombuffer( trace[ 'm' ], dtype = numpy.uint8 )                             ),
          ( 'c',              lambda trace : numpy.frombuffer( trace[ 'c' ], dtype = numpy.uint8 )                             ) ]

    for ( k, f ) in T :
      if ( k in self.trace_content ) :
        fd[ k ][ i ] = f( trace )

  # Driver policy: user-driven

  def _policy_user( self, fd ) :
    n   = 1 * self.trace_count

    self._hdf5_add_attr( fd ) ; self._hdf5_add_data( fd, n )

    ( k, x ) = self.kernel.policy_user_init( self.policy_spec )

    for i in range( n ) :
      self._acquire_log_inc( i, n )
      self._hdf5_set_data( fd, self.acquire( k = k, x = x ), i )
      self._acquire_log_dec( i, n )

      ( k, x ) = self.kernel.policy_user_iter( self.policy_spec, k, x, i )

  # Driver policy: TVLA-driven
  #
  # - mode = fvr_k ~>  fixed-versus random  key
  # - mode = fvr_d ~>  fixed-versus random data  
  # - mode = svr_d ~>   semi-versus random data  
  # - mode = rvr_d ~> random-versus random data  

  def _policy_tvla( self, fd ) :
    n   = 2 * self.trace_count

    lhs = numpy.fromiter( range( 0, int( n / 2 ) ), numpy.int )
    rhs = numpy.fromiter( range( int( n / 2 ), n ), numpy.int )

    if ( 'tvla/lhs' in self.trace_content ) :
      fd[ 'tvla/lhs' ] = lhs
    if ( 'tvla/rhs' in self.trace_content ) :
      fd[ 'tvla/rhs' ] = rhs

    self._hdf5_add_attr( fd ) ; self._hdf5_add_data( fd, n )

    ( k, x ) = self.kernel.policy_tvla_init_lhs( self.policy_spec )

    for i in lhs :
      self._acquire_log_inc( i, n, message = 'lhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )
      self._hdf5_set_data( fd, self.acquire( k = k, x = x ), i )
      self._acquire_log_dec( i, n, message = 'lhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )

      ( k, x ) = self.kernel.policy_tvla_iter_lhs( self.policy_spec, k, x, i )

    ( k, x ) = self.kernel.policy_tvla_init_rhs( self.policy_spec )

    for i in rhs :
      self._acquire_log_inc( i, n, message = 'rhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )
      self._hdf5_set_data( fd, self.acquire( k = k, x = x ), i )
      self._acquire_log_dec( i, n, message = 'rhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )

      ( k, x ) = self.kernel.policy_tvla_iter_rhs( self.policy_spec, k, x, i )

  # Acquire data wrt. this driver, using the kernel model.

  def acquire( self, k = None, x = None ) :
    if   ( self.kernel.func == 'enc' ) :
      return self._acquire_enc( k = k, m = x )
    elif ( self.kernel.func == 'dec' ) :
      return self._acquire_dec( k = k, c = x )

  # Prepare the driver:
  #
  # 1. check the on-board driver
  # 2. query the on-board kernel wrt. the size of 
  # 3. build a model of the on-board kernel
  # 4. check the model supports whatever policy is selected

  def prepare( self ) : 
    if ( self.job.board.driver_version != sca3s_be.share.version.VERSION ) :
      raise Exception( 'mismatched driver version'    )
    if ( self.job.board.driver_id      != 'block'                        ) :
      raise Exception( 'mismatched driver identifier' )

    ( kernel_nameof, kernel_typeof ) = self.job.board.kernel_id.split( '/' )
    
    if ( kernel_nameof not in [ 'generic', 'aes' ] ) :
      raise Exception( 'unsupported kernel name'   )
    if ( kernel_typeof not in [     'enc', 'dec' ] ) :
      raise Exception( 'unsupported kernel type'   )
    
    if ( ( kernel_typeof == 'enc' ) and ( self.job.board.kernel_data_i != set( [ 'r', 'k', 'm' ] ) ) ) :
      raise Exception( 'inconsistent kernel I/O spec.' )
    if ( ( kernel_typeof == 'dec' ) and ( self.job.board.kernel_data_i != set( [ 'r', 'k', 'c' ] ) ) ) :
      raise Exception( 'inconsistent kernel I/O spec.' )
    if ( ( kernel_typeof == 'enc' ) and ( self.job.board.kernel_data_o != set( [ 'c'           ] ) ) ) :
      raise Exception( 'inconsistent kernel I/O spec.' )
    if ( ( kernel_typeof == 'dec' ) and ( self.job.board.kernel_data_o != set( [ 'm'           ] ) ) ) :
      raise Exception( 'inconsistent kernel I/O spec.' )

    kernel_sizeof_r = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '?data r' ) ), 2 ** 8 )
    kernel_sizeof_k = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '?data k' ) ), 2 ** 8 )
    kernel_sizeof_m = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '?data m' ) ), 2 ** 8 )
    kernel_sizeof_c = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '?data c' ) ), 2 ** 8 )
    
    self.job.log.info( '?data r -> kernel sizeof( r ) = %s', kernel_sizeof_r )
    self.job.log.info( '?data k -> kernel sizeof( k ) = %s', kernel_sizeof_k )
    self.job.log.info( '?data m -> kernel sizeof( m ) = %s', kernel_sizeof_m )
    self.job.log.info( '?data c -> kernel sizeof( c ) = %s', kernel_sizeof_c )

    try :
      self.kernel = importlib.import_module( 'sca3s.backend.acquire.kernel'  + '.' + self.job.board.driver_id + '.' + kernel_nameof ).KernelImp( kernel_typeof, kernel_sizeof_r, kernel_sizeof_k, kernel_sizeof_m, kernel_sizeof_c )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % ( 'kernel', self.job.board.kernel_id ) )

    if ( not self.kernel.supports( self.policy_id ) ) :
      raise Exception( 'unsupported kernel policy' )

  # Process the driver:
  #
  # 1. open     HDF5 file
  # 2. execute selected policy
  # 3. close    HDF5 file
  # 4. compress HDF5 file

  def process( self ) :
    fd = h5py.File( os.path.join( self.job.path, 'acquire.hdf5' ), 'a' )

    if   ( self.policy_id == 'user' ) : 
      self._policy_user( fd )
    elif ( self.policy_id == 'tvla' ) : 
      self._policy_tvla( fd )

    fd.close()

    self.job.exec_native( [ 'gzip', '--quiet', os.path.join( self.job.path, 'acquire.hdf5' ) ] )
