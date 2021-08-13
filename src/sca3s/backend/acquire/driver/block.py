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

import binascii, numpy

class DriverImp( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

  # Perform acquisition step: encryption operation

  def _acquire_enc( self, data ) :
    esr = data[ 'esr' ] if ( 'esr' in data ) else None
    k   = data[ 'k'   ] if ( 'k'   in data ) else None
    m   = data[ 'x'   ] if ( 'x'   in data ) else None

    if ( esr == None ) :
      esr = self.job.board.kernel.expand( '{$*|esr|}' )
    if ( k   == None ) :
      k   = self.job.board.kernel.expand( '{$*|k|}'   )
    if ( m   == None ) :
      m   = self.job.board.kernel.expand( '{$*|m|}'   )

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

  def _acquire_dec( self, data ) :
    esr = data[ 'esr' ] if ( 'esr' in data ) else None
    k   = data[ 'k'   ] if ( 'k'   in data ) else None
    c   = data[ 'x'   ] if ( 'x'   in data ) else None

    if ( esr == None ) :
      esr = self.job.board.kernel.expand( '{$*|esr|}' )
    if ( k   == None ) :
      k   = self.job.board.kernel.expand( '{$*|k|}'   )
    if ( c   == None ) :
      c   = self.job.board.kernel.expand( '{$*|c|}'   )

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
   
  def hdf5_add_attr( self, fd              ) :
    spec = [ ( 'sizeof_k', self.job.board.kernel.sizeof_k, '<u8' ),
             ( 'sizeof_m', self.job.board.kernel.sizeof_m, '<u8' ),
             ( 'sizeof_c', self.job.board.kernel.sizeof_c, '<u8' ) ]

    self.job.board.hdf5_add_attr( self.trace_content, fd              )
    self.job.scope.hdf5_add_attr( self.trace_content, fd              )

    sca3s_be.share.util.hdf5_add_attr( spec, self.trace_content, fd              )

  # HDF5 file manipulation: add data
 
  def hdf5_add_data( self, fd, n           ) :
    spec = [ ( 'k', ( n, self.job.board.kernel.sizeof_k ), 'B' ),
             ( 'm', ( n, self.job.board.kernel.sizeof_m ), 'B' ),
             ( 'c', ( n, self.job.board.kernel.sizeof_c ), 'B' ) ]

    self.job.board.hdf5_add_data( self.trace_content, fd, n           )
    self.job.scope.hdf5_add_data( self.trace_content, fd, n           )

    sca3s_be.share.util.hdf5_add_data( spec, self.trace_content, fd, n           )
 
  # HDF5 file manipulation: set data

  def hdf5_set_data( self, fd, n, i, trace ) :
    spec = [ ( 'k', lambda trace : numpy.frombuffer( trace[ 'k' ], dtype = numpy.uint8 ) ),
             ( 'm', lambda trace : numpy.frombuffer( trace[ 'm' ], dtype = numpy.uint8 ) ),
             ( 'c', lambda trace : numpy.frombuffer( trace[ 'c' ], dtype = numpy.uint8 ) ) ]

    self.job.board.hdf5_set_data( self.trace_content, fd, n, i, trace )
    self.job.scope.hdf5_set_data( self.trace_content, fd, n, i, trace )

    sca3s_be.share.util.hdf5_set_data( spec, self.trace_content, fd, n, i, trace )

  # Acquire data wrt. this driver

  def acquire( self, data = dict() ) :
    if   ( self.job.board.kernel.modeof == 'enc' ) :
      return self._acquire_enc( data )
    elif ( self.job.board.kernel.modeof == 'dec' ) :
      return self._acquire_dec( data )

  # Prepare the driver:
  #
  # 1. check the on-board driver for consistency
  # 2. set any defaults
  # 3. check the on-board kernel for consistency

  def prepare( self ) : 
    if ( not sca3s_be.share.version.match( self.job.board.driver_version ) ) :
      raise Exception( 'inconsistent driver version'    )
    if ( self.driver_id !=               ( self.job.board.driver_id      ) ) :
      raise Exception( 'inconsistent driver identifier' )
    
    if ( self.job.board.kernel.nameof not in [ 'generic', 'aes'        ] ) :
      raise Exception( 'unsupported kernel name'   )
    if ( self.job.board.kernel.modeof not in [ 'default', 'enc', 'dec' ] ) :
      raise Exception( 'unsupported kernel type'   )

    if ( self.job.board.kernel.modeof == 'default' ) :
      self.job.board.kernel.modeof = 'enc'

    if ( self.job.board.kernel.modeof == 'enc'     ) :
      if ( not ( self.job.board.kernel.data_wr_id >= set( [        'esr', 'k', 'm' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )
      if ( not ( self.job.board.kernel.data_rd_id >= set( [ 'fec', 'fcc',      'c' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )

    if ( self.job.board.kernel.modeof == 'dec'     ) :
      if ( not ( self.job.board.kernel.data_wr_id >= set( [        'esr', 'k', 'c' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )
      if ( not ( self.job.board.kernel.data_rd_id >= set( [ 'fec', 'fcc',      'm' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )

    if ( not self.job.board.kernel.supports_policy( self.policy_id ) ) :
      raise Exception( 'unsupported kernel policy' )
