# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share  as share

from acquire import board  as board
from acquire import scope  as scope
from acquire import driver as driver

from acquire import repo   as repo
from acquire import depo   as depo

from .       import *

import Crypto.Cipher.AES as AES

class DriverImp( Block ) :
  def __init__( self, job ) :
    super().__init__( job )

  def acquire( self ) :
    k = self.kernel_k
    r = bytes( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_r ) ] )
    m = bytes( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_m ) ] )

    if ( len( k ) > 0 ) :
      self.job.board.interact( '>reg k %s' % share.util.str2octetstr( k ).upper() )
    if ( len( r ) > 0 ) :
      self.job.board.interact( '>reg r %s' % share.util.str2octetstr( r ).upper() )
    if ( len( m ) > 0 ) :
      self.job.board.interact( '>reg m %s' % share.util.str2octetstr( m ).upper() )
  
    _                                  = self.job.scope.acquire( scope.ACQUIRE_MODE_PREPARE )

    self.job.board.interact( '!enc_init' )
    self.job.board.interact( '!enc'      )
  
    ( trigger, signal ) = self.job.scope.acquire( scope.ACQUIRE_MODE_COLLECT )
  
    c = share.util.octetstr2str( self.job.board.interact( '<reg c' ) )

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

    tsc_enc = share.util.seq2int( share.util.octetstr2str( self.job.board.interact( '?tsc' ) ), 2 ** 8 )
    self.job.board.interact( '!nop'      )
    tsc_nop = share.util.seq2int( share.util.octetstr2str( self.job.board.interact( '?tsc' ) ), 2 ** 8 )

    return { 'trigger' : trigger, 'signal' : signal, 'tsc' : tsc_enc - tsc_nop, 'k' : k, 'r' : r, 'm' : m, 'c' : c }
