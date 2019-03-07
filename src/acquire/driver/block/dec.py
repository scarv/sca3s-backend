# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire        import share  as share

from acquire.device import board  as board
from acquire.device import scope  as scope
from acquire        import driver as driver

from acquire        import repo   as repo
from acquire        import depo   as depo

from .              import *

class DriverImp( Block ) :
  def __init__( self, job ) :
    super().__init__( job )

  def _process( self ) :
    k = self.kernel_k
    r = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_r ) ] )
    c = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_c ) ] )

    if ( len( k ) > 0 ) :
      self.job.device_board.interact( '>reg k %s' % share.util.str2octetstr( k ).upper() )
    if ( len( r ) > 0 ) :
      self.job.device_board.interact( '>reg r %s' % share.util.str2octetstr( r ).upper() )
    if ( len( c ) > 0 ) :
      self.job.device_board.interact( '>reg c %s' % share.util.str2octetstr( c ).upper() )
  
    _                                  = self.job.device_scope.acquire( scope.ACQUIRE_MODE_PREPARE )
  
    self.job.device_board.interact( '!dec_init' )
    self.job.device_board.interact( '!dec'      )
  
    ( signal_trigger, signal_acquire ) = self.job.device_scope.acquire( scope.ACQUIRE_MODE_COLLECT )
  
    m = share.util.octetstr2str( self.job.device_board.interact( '<reg m' ) )

    tsc_dec = share.util.seq2int( share.util.octetstr2str( self.job.device_board.interact( '?tsc' ) ), 2 ** 8 )
    self.job.device_board.interact( '!nop'      )
    tsc_nop = share.util.seq2int( share.util.octetstr2str( self.job.device_board.interact( '?tsc' ) ), 2 ** 8 )
    
    return share.trace.Trace( signal_trigger, signal_acquire, tsc = tsc_dec - tsc_nop, data_i = { 'k' : k, 'r' : r, 'c' : c }, data_o = { 'm' : m } )
