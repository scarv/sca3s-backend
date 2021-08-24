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

import binascii, h5py, numpy

class DriverImp( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

  def _acquire( self, data ) :
    esr = data[ 'esr' ] if ( 'esr' in data ) else None
    m   = data[ 'm'   ] if ( 'm'   in data ) else None

    if ( esr == None ) :
      esr = self.job.board.kernel.expand( '{$*|esr|}' )
    if ( m   == None ) :
      m   = self.job.board.kernel.expand( '{$*|m|}'   )

    self.job.board.interact( '>data esr %s' % sca3s_be.share.util.str2octetstr( esr ).upper() )
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
  
    d = sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data d' ) )

    sca3s_be.share.sys.log.debug( 'acquire : esr = %s', binascii.b2a_hex( esr ) )
    sca3s_be.share.sys.log.debug( 'acquire : m   = %s', binascii.b2a_hex( m   ) )
    sca3s_be.share.sys.log.debug( 'acquire : d   = %s', binascii.b2a_hex( d   ) )

    if ( ( self.job.board.board_mode == 'interactive' ) and self.job.board.kernel.supports_model() ) :
      if ( self.job.board.kernel.model( m ) != d ) :
        raise Exception( 'failed I/O verification => model( m ) != d' )

    return { 'trace/trigger' : trigger, 'trace/signal' : signal, 
             'edge/pos' : edge_pos, 'edge/neg' : edge_neg, 
             'perf/cycle' : cycle_enc - cycle_nop, 'perf/duration' : duration, 
             'data/m' : m, 'data/d' : d }

  def hdf5_add_attr( self, fd              ) :
    spec = [ ( 'kernel/sizeof_m',      self.job.board.kernel.sizeof_m,   '<u8' ),
             ( 'kernel/sizeof_d',      self.job.board.kernel.sizeof_d,   '<u8' ) ]

    self.job.board.hdf5_add_attr( self.trace_content, fd              )
    self.job.scope.hdf5_add_attr( self.trace_content, fd              )

    sca3s_be.share.util.hdf5_add_attr( spec, self.trace_content, fd              )

  def hdf5_add_data( self, fd, n           ) :
    spec = [ (   'data/m',        ( n, self.job.board.kernel.sizeof_m ), 'B'   ),
             (   'data/usedof_m', ( n,                                ), '<u8' ),
             (   'data/d',        ( n, self.job.board.kernel.sizeof_d ), 'B'   ),
             (   'data/usedof_d', ( n,                                ), '<u8' ) ]

    self.job.board.hdf5_add_data( self.trace_content, fd, n           )
    self.job.scope.hdf5_add_data( self.trace_content, fd, n           )

    sca3s_be.share.util.hdf5_add_data( spec, self.trace_content, fd, n           )

  def hdf5_set_data( self, fd, n, i, trace ) :
    spec = [ (   'data/m',        lambda trace : numpy.frombuffer( trace[ 'data/m' ], dtype = numpy.uint8 ) ),
             (   'data/usedof_m', lambda trace :              len( trace[ 'data/m' ]                      ) ),
             (   'data/d',        lambda trace : numpy.frombuffer( trace[ 'data/d' ], dtype = numpy.uint8 ) ),
             (   'data/usedof_d', lambda trace :              len( trace[ 'data/d' ]                      ) ) ]

    self.job.board.hdf5_set_data( self.trace_content, fd, n, i, trace )
    self.job.scope.hdf5_set_data( self.trace_content, fd, n, i, trace )

    sca3s_be.share.util.hdf5_set_data( spec, self.trace_content, fd, n, i, trace )

  def acquire( self, data = dict() ) :
    return self._acquire( data )

  def prepare( self ) : 
    if ( not sca3s_be.share.version.match( self.job.board.driver_version ) ) :
      raise Exception( 'inconsistent driver version'    )
    if ( self.driver_id !=               ( self.job.board.driver_id      ) ) :
      raise Exception( 'inconsistent driver identifier' )
    
    if ( self.job.board.kernel.nameof not in [ 'generic' ] ) :
      raise Exception( 'unsupported kernel name'   )
    if ( self.job.board.kernel.modeof not in [ 'default' ] ) :
      raise Exception( 'unsupported kernel type'   )

    if ( self.job.board.kernel.modeof == 'default' ) :
      if ( not ( self.job.board.kernel.data_wr_id >= set( [        'esr', 'm' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )
      if ( not ( self.job.board.kernel.data_rd_id >= set( [ 'fec', 'fcc', 'd' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )

    if ( ( self.policy_id == 'user' ) and not self.job.board.kernel.supports_policy_user( self.policy_spec ) ) :
      raise Exception( 'unsupported kernel policy' )
    if ( ( self.policy_id == 'tvla' ) and not self.job.board.kernel.supports_policy_tvla( self.policy_spec ) ) :
      raise Exception( 'unsupported kernel policy' )
