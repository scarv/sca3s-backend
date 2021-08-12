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

import binascii, h5py, numpy, os

class DriverImp( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.trace_spec    = self.job.conf.get( 'trace_spec' )

    self.trace_content =       self.trace_spec.get( 'content' )
    self.trace_count   =  int( self.trace_spec.get( 'count'   ) )

    self.policy_id     = self.driver_spec.get( 'policy_id'   )
    self.policy_spec   = self.driver_spec.get( 'policy_spec' )

  # Perform acquisition step: encryption operation

  def _acquire_enc( self, esr = None, k = None, m = None ) :
    if ( esr == None ) :
      esr = self._expand( '{$*|esr|}' )
    if ( k   == None ) :
      k   = self._expand( '{$*|k|}'   )
    if ( m   == None ) :
      m   = self._expand( '{$*|m|}'   )

    self.job.board.interact( '>data esr %s' % sca3s_be.share.util.str2octetstr( esr ).upper() )
    self.job.board.interact( '>data k %s'   % sca3s_be.share.util.str2octetstr( k   ).upper() )
    self.job.board.interact( '>data m %s'   % sca3s_be.share.util.str2octetstr( m   ).upper() )
  
    _                   = self.job.scope.acquire( mode = scope.ACQUIRE_MODE_PRIME )

    self.job.board.interact( '!kernel_prologue' )

    self.job.board.interact( '!kernel'          )
    cycle_enc = sca3s_be.share.util.octetstr2int( self.job.board.interact( '<data fcc' ) )
    self.job.board.interact( '!kernel_nop' )
    cycle_nop = sca3s_be.share.util.octetstr2int( self.job.board.interact( '<data fcc' ) )

    self.job.board.interact( '!kernel_epilogue' )
  
    ( trigger, signal ) = self.job.scope.acquire( mode = scope.ACQUIRE_MODE_FETCH )
    ( edge_pos, edge_neg, duration ) = self._measure( trigger )
  
    c = sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data c' ) )

    sca3s_be.share.sys.log.debug( 'acquire : esr = %s', binascii.b2a_hex( esr ) )
    sca3s_be.share.sys.log.debug( 'acquire : k   = %s', binascii.b2a_hex( k   ) )
    sca3s_be.share.sys.log.debug( 'acquire : m   = %s', binascii.b2a_hex( m   ) )
    sca3s_be.share.sys.log.debug( 'acquire : c   = %s', binascii.b2a_hex( c   ) )

    if ( ( self.job.board.board_mode == 'interactive' ) and self.job.board.kernel.supports_kernel() ) :
      if ( self.job.board.kernel.kernel_enc( k, m ) != c ) :
        raise Exception( 'failed I/O verification => enc( k, m ) != c' )

    return { 'trace/trigger' : trigger, 'trace/signal' : signal, 'edge/pos' : edge_pos, 'edge/neg' : edge_neg, 'perf/cycle' : cycle_enc - cycle_nop, 'perf/duration' : duration, 'k' : k, 'm' : m, 'c' : c }

  # Perform acquisition step: decryption operation

  def _acquire_dec( self, esr = None, k = None, c = None ) :
    if ( esr == None ) :
      esr = self._expand( '{$*|esr|}' )
    if ( k   == None ) :
      k   = self._expand( '{$*|k|}'   )
    if ( c   == None ) :
      c   = self._expand( '{$*|c|}'   )

    self.job.board.interact( '>data esr %s' % sca3s_be.share.util.str2octetstr( esr ).upper() )
    self.job.board.interact( '>data k %s'   % sca3s_be.share.util.str2octetstr( k   ).upper() )
    self.job.board.interact( '>data c %s'   % sca3s_be.share.util.str2octetstr( c   ).upper() )
  
    _                   = self.job.scope.acquire( mode = scope.ACQUIRE_MODE_PRIME )
  
    self.job.board.interact( '!kernel_prologue' )

    self.job.board.interact( '!kernel'          )
    cycle_dec = sca3s_be.share.util.octetstr2int( self.job.board.interact( '<data fcc' ) )
    self.job.board.interact( '!kernel_nop'      )
    cycle_nop = sca3s_be.share.util.octetstr2int( self.job.board.interact( '<data fcc' ) )

    self.job.board.interact( '!kernel_epilogue' )
  
    ( trigger, signal ) = self.job.scope.acquire( mode = scope.ACQUIRE_MODE_FETCH )
    ( edge_pos, edge_neg, duration ) = self._measure( trigger )
  
    m = sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data m' ) )

    sca3s_be.share.sys.log.debug( 'acquire : esr = %s', binascii.b2a_hex( esr ) )
    sca3s_be.share.sys.log.debug( 'acquire : k   = %s', binascii.b2a_hex( k   ) )
    sca3s_be.share.sys.log.debug( 'acquire : c   = %s', binascii.b2a_hex( c   ) )
    sca3s_be.share.sys.log.debug( 'acquire : m   = %s', binascii.b2a_hex( m   ) )

    if ( ( self.job.board.board_mode == 'interactive' ) and self.job.board.kernel.supports_kernel() ) :
      if ( self.job.board.kernel.kernel_dec( k, c ) != m ) :
        raise Exception( 'failed I/O verification => dec( k, c ) != m' )

    return { 'trace/trigger' : trigger, 'trace/signal' : signal, 'edge/pos' : edge_pos, 'edge/neg' : edge_neg, 'perf/cycle' : cycle_dec - cycle_nop, 'perf/duration' : duration, 'k' : k, 'c' : c, 'm' : m } 

  # HDF5 file manipulation: add attributes
   
  def _hdf5_add_attr( self, fd              ) :
    spec = [ ( 'kernel_sizeof_k', self.job.board.kernel.sizeof_k, '<u8' ),
             ( 'kernel_sizeof_m', self.job.board.kernel.sizeof_m, '<u8' ),
             ( 'kernel_sizeof_c', self.job.board.kernel.sizeof_c, '<u8' ) ]
    
    super()._hdf5_add_attr( spec, self.trace_content, fd              )

  # HDF5 file manipulation: add data
 
  def _hdf5_add_data( self, fd, n           ) :
    spec = [ ( 'k', ( n, self.job.board.kernel.sizeof_k ), 'B' ),
             ( 'm', ( n, self.job.board.kernel.sizeof_m ), 'B' ),
             ( 'c', ( n, self.job.board.kernel.sizeof_c ), 'B' ) ]

    super()._hdf5_add_data( spec, self.trace_content, fd, n           )
 
  # HDF5 file manipulation: set data

  def _hdf5_set_data( self, fd, n, i, trace ) :
    spec = [ ( 'k', lambda trace : numpy.frombuffer( trace[ 'k' ], dtype = numpy.uint8 ) ),
             ( 'm', lambda trace : numpy.frombuffer( trace[ 'm' ], dtype = numpy.uint8 ) ),
             ( 'c', lambda trace : numpy.frombuffer( trace[ 'c' ], dtype = numpy.uint8 ) ) ]

    super()._hdf5_set_data( spec, self.trace_content, fd, n, i, trace )

  # Driver policy: user-driven

  def _policy_user( self, fd ) :
    n   = 1 * self.trace_count

    self._hdf5_add_attr( fd ) ; self._hdf5_add_data( fd, n )

    ( k, x ) = self._expand( self.job.board.kernel.policy_user_init( self.policy_spec ) )

    for i in range( n ) :
      self._acquire_log_inc( n, i )
      self._hdf5_set_data( fd, n, i, self.acquire( k = k, x = x ) )
      self._acquire_log_dec( n, i )

      ( k, x ) = self._expand( self.job.board.kernel.policy_user_iter( self.policy_spec, n, i, k, x ) )

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

    ( k, x ) = self._expand( self.job.board.kernel.policy_tvla_init_lhs( self.policy_spec ) )

    for i in lhs :
      self._acquire_log_inc( n, i, message = 'lhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )
      self._hdf5_set_data( fd, n, i, self.acquire( k = k, x = x ) )
      self._acquire_log_dec( n, i, message = 'lhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )

      ( k, x ) = self._expand( self.job.board.kernel.policy_tvla_iter_lhs( self.policy_spec, n, i, k, x ) )

    ( k, x ) = self._expand( self.job.board.kernel.policy_tvla_init_rhs( self.policy_spec ) )

    for i in rhs :
      self._acquire_log_inc( n, i, message = 'rhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )
      self._hdf5_set_data( fd, n, i, self.acquire( k = k, x = x ) )
      self._acquire_log_dec( n, i, message = 'rhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )

      ( k, x ) = self._expand( self.job.board.kernel.policy_tvla_iter_rhs( self.policy_spec, n, i, k, x ) )

  # Post-processing, aka. fixed-function analysis: CI 

  def _analyse_ci( self ) :    
    doc = sca3s_be.share.report.Report( self.job )

    self.job.log.indent_inc( message = 'generate report preamble' )
    doc.emit_preamble()
    self.job.log.indent_dec()
    self.job.log.indent_inc( message = 'generate report prologue' )
    doc.emit_prologue()
    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'generate report content: calibration report' )
    doc.emit_section_calibrate()
    self.job.log.indent_dec()
    self.job.log.indent_inc( message = 'generate report content: latency     report' )
    doc.emit_section_latency()
    self.job.log.indent_dec()
    self.job.log.indent_inc( message = 'generate report content: leakage     report' )
    doc.emit_section_leakage()
    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'generate report epilogue' )
    doc.emit_epilogue()
  
    self.job.log.indent_inc( message = 'compile  report'          )
    doc.compile( os.path.join( self.job.path, 'acquire.pdf' ) )
    self.job.log.indent_dec()
    
    self.job.result_transfer[ 'acquire.pdf' ] = { 'ContentType': 'application/pdf', 'CacheControl': 'no-cache, max-age=0', 'ACL': 'public-read' }

  # Post-processing, aka. fixed-function analysis: contest

  def _analyse_contest( self ) :
    self.job.result_response[ 'score' ] = 0

  # Acquire data wrt. this driver

  def acquire( self, k = None, x = None ) :
    if   ( self.job.board.kernel.typeof == 'enc' ) :
      return self._acquire_enc( k = k, m = x )
    elif ( self.job.board.kernel.typeof == 'dec' ) :
      return self._acquire_dec( k = k, c = x )

  # Prepare the driver:
  #
  # 1. check the on-board driver for consistency
  # 2. check the on-board kernel for consistency
  # 3. check the kernel model supports whatever policy is selected

  def prepare( self ) : 
    if ( not sca3s_be.share.version.match( self.job.board.driver_version ) ) :
      raise Exception( 'inconsistent driver version'    )
    if ( self.driver_id !=               ( self.job.board.driver_id      ) ) :
      raise Exception( 'inconsistent driver identifier' )
    
    if ( self.job.board.kernel.nameof not in [ 'generic', 'aes' ] ) :
      raise Exception( 'unsupported kernel name'   )
    if ( self.job.board.kernel.typeof not in [     'enc', 'dec' ] ) :
      raise Exception( 'unsupported kernel type'   )

    if ( self.job.board.kernel.typeof == 'enc' ) :
      if ( not ( self.job.board.kernel.data_wr_id >= set( [        'esr', 'k', 'm' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )
      if ( not ( self.job.board.kernel.data_rd_id >= set( [ 'fec', 'fcc',      'c' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )

    if ( self.job.board.kernel.typeof == 'dec' ) :
      if ( not ( self.job.board.kernel.data_wr_id >= set( [        'esr', 'k', 'c' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )
      if ( not ( self.job.board.kernel.data_rd_id >= set( [ 'fec', 'fcc',      'm' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )

    if ( not self.job.board.kernel.supports_policy( self.policy_id ) ) :
      raise Exception( 'unsupported kernel policy' )

  # Execute the driver prologue

  def execute_prologue( self ) :
    pass

  # Execute the driver

  def execute( self ) :
    fd = h5py.File( os.path.join( self.job.path, 'acquire.hdf5' ), 'a' )

    if   ( self.policy_id == 'user' ) : 
      self._policy_user( fd )
    elif ( self.policy_id == 'tvla' ) : 
      self._policy_tvla( fd )

    fd.close()

  # Execute the driver epilogue

  def execute_epilogue( self ) :
    if   ( self.job.type == 'user'    ) :
      pass
    elif ( self.job.type == 'ci'      ) :
      self._analyse_ci()
    elif ( self.job.type == 'contest' ) :
      self._analyse_contest()

    self.job.exec_native( [ 'gzip', '--quiet', os.path.join( self.job.path, 'acquire.hdf5' ) ] )

