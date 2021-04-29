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

    if ( self.driver_spec.get( 'verify' ) and self.job.board.board_mode == 'interactive' ) :
      t = self.kernel.enc( k, m )

      if ( ( t != None ) and ( t != c ) ) :
        raise Exception( 'failed I/O verification => enc( k, m ) != c' )  

    cycle_enc = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data tsc' ) ), 2 ** 8 )
    self.job.board.interact( '!nop' )
    cycle_nop = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data tsc' ) ), 2 ** 8 )

    ( edge_pos, edge_neg, duration ) = self._measure( trigger )

    return { 'trace/trigger' : trigger, 'trace/signal' : signal, 'edge/pos' : edge_pos, 'edge/neg' : edge_neg, 'perf/cycle' : cycle_enc - cycle_nop, 'perf/duration' : duration, 'r' : r, 'k' : k, 'm' : m, 'c' : c }

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

    if ( self.driver_spec.get( 'verify' ) and self.job.board.board_mode == 'interactive' ) :
      t = self.kernel.dec( k, c )

      if ( ( t != None ) and ( t != m ) ) :
        raise Exception( 'failed I/O verification => dec( k, c ) != m' )  

      elif ( self.job.board.board_mode == 'non-interactive' ) :
        self.job.log.info( 'skipping non-interactive I/O verification' )

    cycle_dec = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data tsc' ) ), 2 ** 8 )
    self.job.board.interact( '!nop' )
    cycle_nop = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data tsc' ) ), 2 ** 8 )

    ( edge_pos, edge_neg, duration ) = self._measure( trigger )

    return { 'trace/trigger' : trigger, 'trace/signal' : signal, 'edge/pos' : edge_pos, 'edge/neg' : edge_neg, 'perf/cycle' : cycle_dec - cycle_nop, 'perf/duration' : duration, 'r' : r, 'k' : k, 'm' : m, 'c' : c } 

  # HDF5 file manipulation: add attributes
   
  def _hdf5_add_attr( self, fd, ks           ) :
    T = [ ( 'kernel_sizeof_k', self.kernel.sizeof_k, '<u8' ),
          ( 'kernel_sizeof_r', self.kernel.sizeof_r, '<u8' ),
          ( 'kernel_sizeof_m', self.kernel.sizeof_m, '<u8' ),
          ( 'kernel_sizeof_c', self.kernel.sizeof_c, '<u8' ) ]
    
    self.job.board.hdf5_add_attr( fd, ks           )
    self.job.scope.hdf5_add_attr( fd, ks           )

    for ( k, v, t ) in T :
      fd.attrs.create( k, v, dtype = t )

  # HDF5 file manipulation: add data

  def _hdf5_add_data( self, fd, ks, n        ) :
    T = [ ( 'r', ( n, self.kernel.sizeof_r ), 'B' ),
          ( 'k', ( n, self.kernel.sizeof_k ), 'B' ),
          ( 'm', ( n, self.kernel.sizeof_m ), 'B' ),
          ( 'c', ( n, self.kernel.sizeof_c ), 'B' ) ]

    self.job.board.hdf5_add_data( fd, ks, n        )
    self.job.scope.hdf5_add_data( fd, ks, n        )

    for ( k, v, t ) in T :
      if ( k in ks ) :
        fd.create_dataset( k, v, t )
 
  # HDF5 file manipulation: set data

  def _hdf5_set_data( self, fd, ks, i, trace ) :
    T = [ ( 'r', lambda trace : numpy.frombuffer( trace[ 'r' ], dtype = numpy.uint8 ) ),
          ( 'k', lambda trace : numpy.frombuffer( trace[ 'k' ], dtype = numpy.uint8 ) ),
          ( 'm', lambda trace : numpy.frombuffer( trace[ 'm' ], dtype = numpy.uint8 ) ),
          ( 'c', lambda trace : numpy.frombuffer( trace[ 'c' ], dtype = numpy.uint8 ) ) ]

    self.job.board.hdf5_set_data( fd, ks, i, trace )
    self.job.scope.hdf5_set_data( fd, ks, i, trace )

    for ( k, f ) in T :
      if ( ( k in ks ) and ( k in trace ) ) :
        fd[ k ][ i ] = f( trace )

  # Driver policy: user-driven

  def _policy_user( self, fd ) :
    n   = 1 * self.trace_count

    self._hdf5_add_attr( fd, self.trace_content ) ; self._hdf5_add_data( fd, self.trace_content, n )

    ( k, x ) = self.kernel.policy_user_init( self.policy_spec )

    for i in range( n ) :
      self._acquire_log_inc( i, n )
      self._hdf5_set_data( fd, self.trace_content, i, self.acquire( k = k, x = x ) )
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

    self._hdf5_add_attr( fd, self.trace_content ) ; self._hdf5_add_data( fd, self.trace_content, n )

    ( k, x ) = self.kernel.policy_tvla_init_lhs( self.policy_spec )

    for i in lhs :
      self._acquire_log_inc( i, n, message = 'lhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )
      self._hdf5_set_data( fd, self.trace_content, i, self.acquire( k = k, x = x ) )
      self._acquire_log_dec( i, n, message = 'lhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )

      ( k, x ) = self.kernel.policy_tvla_iter_lhs( self.policy_spec, k, x, i )

    ( k, x ) = self.kernel.policy_tvla_init_rhs( self.policy_spec )

    for i in rhs :
      self._acquire_log_inc( i, n, message = 'rhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )
      self._hdf5_set_data( fd, self.trace_content, i, self.acquire( k = k, x = x ) )
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
    if ( not sca3s_be.share.version.match( self.job.board.driver_version ) ) :
      raise Exception( 'inconsistent driver version'    )
    if ( self.job.board.driver_id != 'block' ) :
      raise Exception( 'inconsistent driver identifier' )

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

    kernel_module   = 'sca3s.backend.acquire.kernel'  + '.' + self.job.board.driver_id + '.' + kernel_nameof

    try :
      self.kernel = importlib.import_module( kernel_module ).KernelImp( kernel_typeof, kernel_sizeof_r, kernel_sizeof_k, kernel_sizeof_m, kernel_sizeof_c )
    except :
      raise ImportError( 'failed to construct %s instance' % ( kernel_module ) )

    if ( not self.kernel.supports( self.policy_id ) ) :
      raise Exception( 'unsupported kernel policy' )

  # Execute the driver prologue.

  def execute_prologue( self ) :
    pass

  # Execute the driver.

  def execute( self ) :
    fd = h5py.File( os.path.join( self.job.path, 'acquire.hdf5' ), 'a' )

    if   ( self.policy_id == 'user' ) : 
      self._policy_user( fd )
    elif ( self.policy_id == 'tvla' ) : 
      self._policy_tvla( fd )

    fd.close()

  # Execute the driver epilogue.

  def execute_epilogue( self ) :
    if   ( self.job.job_type == 'user'    ) :
      pass
    elif ( self.job.job_type == 'ci'      ) :
      pass
    elif ( self.job.job_type == 'contest' ) :
      pass

    self.job.exec_native( [ 'gzip', '--quiet', os.path.join( self.job.path, 'acquire.hdf5' ) ] )
