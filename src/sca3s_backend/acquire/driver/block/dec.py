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
    c = bytes( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_c ) ] )

    if ( len( k ) > 0 ) :
      self.job.board.interact( '>reg k %s' % be.share.util.str2octetstr( k ).upper() )
    if ( len( r ) > 0 ) :
      self.job.board.interact( '>reg r %s' % be.share.util.str2octetstr( r ).upper() )
    if ( len( c ) > 0 ) :
      self.job.board.interact( '>reg c %s' % be.share.util.str2octetstr( c ).upper() )
  
    _                                  = self.job.scope.acquire( scope.ACQUIRE_MODE_PREPARE )
  
    self.job.board.interact( '!dec_init' )
    self.job.board.interact( '!dec'      )
  
    ( trigger, signal ) = self.job.scope.acquire( scope.ACQUIRE_MODE_COLLECT )
  
    m = be.share.util.octetstr2str( self.job.board.interact( '<reg m' ) )

    if ( self.driver_spec.get( 'verify' ) ) :
      if   ( self.kernel_id == 'aes-128' ) :
        if ( m != AES.new( k ).decrypt( c ) ) :
          raise Exception()  
      elif ( self.kernel_id == 'aes-192' ) :
        if ( m != AES.new( k ).decrypt( c ) ) :
          raise Exception()  
      elif ( self.kernel_id == 'aes-256' ) :
        if ( m != AES.new( k ).decrypt( c ) ) :
          raise Exception()  

    tsc_dec = be.share.util.seq2int( be.share.util.octetstr2str( self.job.board.interact( '?tsc' ) ), 2 ** 8 )
    self.job.board.interact( '!nop'      )
    tsc_nop = be.share.util.seq2int( be.share.util.octetstr2str( self.job.board.interact( '?tsc' ) ), 2 ** 8 )

    return { 'trigger' : trigger, 'signal' : signal, 'tsc' : tsc_dec - tsc_nop, 'k' : k, 'r' : r, 'm' : m, 'c' : c }    
