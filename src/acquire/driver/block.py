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

import random

class DriverImp( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

  def _interact( self, k, r, m ) :
    if ( len( k ) > 0 ) :
      self.job.device_board.interact( '>reg k %s' % share.util.str2octetstr( k ).upper() )
    if ( len( r ) > 0 ) :
      self.job.device_board.interact( '>reg r %s' % share.util.str2octetstr( r ).upper() )
    if ( len( m ) > 0 ) :
      self.job.device_board.interact( '>reg m %s' % share.util.str2octetstr( m ).upper() )
  
    _                                  = self.job.device_scope.acquire( scope.ACQUIRE_MODE_PREPARE )
  
    self.job.device_board.interact( '!enc_init' )
    self.job.device_board.interact( '!enc'      )
  
    ( signal_trigger, signal_acquire ) = self.job.device_scope.acquire( scope.ACQUIRE_MODE_COLLECT )
  
    c = share.util.octetstr2str( self.job.device_board.interact( '<reg c' ) )
  
    return ( c, signal_trigger, signal_acquire )

  def _process_prologue( self ) : 
    t = self.job.device_board.interact( '?id' ).split( ':' )

    if ( len( t ) != 3 ) :
      raise Exception()

    self.driver_type       =      t[ 0 ]
    self.driver_version    =      t[ 1 ]

    t = t[ 2 ].split( ',' )

    if ( len( t ) != 3 ) :
      raise Exception()

    self.kernel_sizeof_rnd = int( t[ 0 ] )
    self.kernel_sizeof_key = int( t[ 1 ] )
    self.kernel_sizeof_blk = int( t[ 2 ] )

    self.job.log.info( 'driver type        = %s', self.driver_type    )
    self.job.log.info( 'driver version     = %s', self.driver_version )

    self.job.log.info( 'driver sizeof( r ) = %s', self.kernel_sizeof_rnd )
    self.job.log.info( 'driver sizeof( k ) = %s', self.kernel_sizeof_key )
    self.job.log.info( 'driver sizeof( m ) = %s', self.kernel_sizeof_blk )
    self.job.log.info( 'driver sizeof( c ) = %s', self.kernel_sizeof_blk )

    if ( self.driver_type    != 'block'         ) :
      raise Exception()
    if ( self.driver_version != share.version.VERSION ) :
      raise Exception()

    self.kernel_key = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_key ) ] )

  def _process( self ) : 
    k = self.kernel_key

    r = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_rnd ) ] )
    m = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_blk ) ] )

    ( c, signal_trigger, signal_acquire ) = self._interact( k, r, m )
  
    return share.trace.Trace( signal_trigger, signal_acquire, data_in = { 'k' : k, 'r' : r, 'm' : m }, data_out = { 'c' : c } )

  def _process_epilogue( self ) : 
    pass
