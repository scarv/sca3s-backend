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

from .                     import *

import Crypto.Cipher.AES as AES

class DriverImp( Block ) :
  def __init__( self, job ) :
    super().__init__( job )

  def acquire( self, k = None, r = None, c = None, m = None ) :
    if ( k == None ) :
      k = self._value( '{$*|k|}' )
    if ( r == None ) :
      r = self._value( '{$*|r|}' )
    if ( c == None ) :
      c = self._value( '{$*|c|}' )

    self.job.board.interact( '>reg k %s' % be.share.util.str2octetstr( k ).upper() )
    self.job.board.interact( '>reg r %s' % be.share.util.str2octetstr( r ).upper() )
    self.job.board.interact( '>reg c %s' % be.share.util.str2octetstr( c ).upper() )
  
    _                   = self.job.scope.prepare()
  
    self.job.board.interact( '!dec_init' )
    self.job.board.interact( '!dec'      )
  
    ( trigger, signal ) = self.job.scope.acquire()
  
    m = be.share.util.octetstr2str( self.job.board.interact( '<reg m' ) )

    be.share.sys.log.debug( 'acquire : k = %s', binascii.b2a_hex( k ) )
    be.share.sys.log.debug( 'acquire : r = %s', binascii.b2a_hex( r ) )
    be.share.sys.log.debug( 'acquire : c = %s', binascii.b2a_hex( c ) )
    be.share.sys.log.debug( 'acquire : m = %s', binascii.b2a_hex( m ) )

    if ( self.driver_spec.get( 'verify' ) ) :
      if   ( ( self.job.board.kernel_id == 'aes' ) and ( self.kernel_sizeof_k == 16 ) ) :
        if ( m != AES.new( k ).decrypt( c ) ) :
          raise Exception()  
      elif ( ( self.job.board.kernel_id == 'aes' ) and ( self.kernel_sizeof_k == 24 ) ) :
        if ( m != AES.new( k ).decrypt( c ) ) :
          raise Exception()  
      elif ( ( self.job.board.kernel_id == 'aes' ) and ( self.kernel_sizeof_k == 32 ) ) :
        if ( m != AES.new( k ).decrypt( c ) ) :
          raise Exception()  

    cycle_dec = be.share.util.seq2int( be.share.util.octetstr2str( self.job.board.interact( '?tsc' ) ), 2 ** 8 )
    self.job.board.interact( '!nop'      )
    cycle_nop = be.share.util.seq2int( be.share.util.octetstr2str( self.job.board.interact( '?tsc' ) ), 2 ** 8 )

    ( edge_hi, edge_lo, duration ) = self._measure( trigger )

    return { 'trace/trigger' : trigger, 'trace/signal' : signal, 'edge/hi' : edge_hi, 'edge/lo' : edge_lo, 'perf/cycle' : cycle_dec - cycle_nop, 'perf/duration' : duration, 'k' : k, 'r' : r, 'm' : m, 'c' : c }    
