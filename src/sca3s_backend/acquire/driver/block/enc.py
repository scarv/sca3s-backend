# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

import sca3s_backend as be
import sca3s_spec    as spec

from sca3s_backend.acquire import board  as board
from sca3s_backend.acquire import scope  as scope
from sca3s_backend.acquire import driver as driver

from sca3s_backend.acquire import repo   as repo
from sca3s_backend.acquire import depo   as depo

from .                     import *

import Crypto.Cipher.AES as AES

class DriverImp( Block ) :
  def __init__( self, job ) :
    super().__init__( job )

  def acquire( self ) :
    k = self.kernel_k
    r = bytes( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_r ) ] )
    m = bytes( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_m ) ] )

    if ( len( k ) > 0 ) :
      self.job.board.interact( '>reg k %s' % be.share.util.str2octetstr( k ).upper() )
    if ( len( r ) > 0 ) :
      self.job.board.interact( '>reg r %s' % be.share.util.str2octetstr( r ).upper() )
    if ( len( m ) > 0 ) :
      self.job.board.interact( '>reg m %s' % be.share.util.str2octetstr( m ).upper() )
  
    _                                  = self.job.scope.acquire( scope.ACQUIRE_MODE_PREPARE )

    self.job.board.interact( '!enc_init' )
    self.job.board.interact( '!enc'      )
  
    ( trigger, signal ) = self.job.scope.acquire( scope.ACQUIRE_MODE_COLLECT )
  
    c = be.share.util.octetstr2str( self.job.board.interact( '<reg c' ) )

    if ( self.driver_spec.get( 'verify' ) ) :
      if   ( self.kernel_id == 'aes-128' ) :
        if ( c != AES.new( k ).encrypt( m ) ) :
          raise Exception()  
      elif ( self.kernel_id == 'aes-192' ) :
        if ( c != AES.new( k ).encrypt( m ) ) :
          raise Exception() 
      elif ( self.kernel_id == 'aes-256' ) :
        if ( c != AES.new( k ).encrypt( m ) ) :
          raise Exception()  

    tsc_enc = be.share.util.seq2int( be.share.util.octetstr2str( self.job.board.interact( '?tsc' ) ), 2 ** 8 )
    self.job.board.interact( '!nop'      )
    tsc_nop = be.share.util.seq2int( be.share.util.octetstr2str( self.job.board.interact( '?tsc' ) ), 2 ** 8 )

    return { 'trigger' : trigger, 'signal' : signal, 'tsc' : tsc_enc - tsc_nop, 'k' : k, 'r' : r, 'm' : m, 'c' : c }
