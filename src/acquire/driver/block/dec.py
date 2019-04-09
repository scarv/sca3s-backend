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

class DriverImp( Block ) :
  def __init__( self, job ) :
    super().__init__( job )

  def _process( self ) :
    k = self.kernel_k
    r = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_r ) ] )
    c = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_c ) ] )

    if ( len( k ) > 0 ) :
      self.job.board.interact( '>reg k %s' % share.util.str2octetstr( k ).upper() )
    if ( len( r ) > 0 ) :
      self.job.board.interact( '>reg r %s' % share.util.str2octetstr( r ).upper() )
    if ( len( c ) > 0 ) :
      self.job.board.interact( '>reg c %s' % share.util.str2octetstr( c ).upper() )
  
    _                                  = self.job.scope.acquire( scope.ACQUIRE_MODE_PREPARE )
  
    self.job.board.interact( '!dec_init' )
    self.job.board.interact( '!dec'      )
  
    ( trigger, signal ) = self.job.scope.acquire( scope.ACQUIRE_MODE_COLLECT )
  
    m = share.util.octetstr2str( self.job.board.interact( '<reg m' ) )

    tsc_dec = share.util.seq2int( share.util.octetstr2str( self.job.board.interact( '?tsc' ) ), 2 ** 8 )
    self.job.board.interact( '!nop'      )
    tsc_nop = share.util.seq2int( share.util.octetstr2str( self.job.board.interact( '?tsc' ) ), 2 ** 8 )

    return { 'trigger' : trigger, 'signal' : signal, 'tsc' : tsc_enc - tsc_nop, 'k' : k, 'r' : r, 'm' : m, 'c' : c }    
