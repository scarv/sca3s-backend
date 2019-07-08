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

import random

class Block( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

  def prepare( self ) : 
    t = self.job.board.interact( '?id' ).split( ':' )

    if ( len( t ) != 3 ) :
      raise Exception()

    self.driver_version = t[ 0 ]
    self.driver_id      = t[ 1 ]
    self.kernel_id      = t[ 2 ]

    self.job.log.info( 'driver version     = %s', self.driver_version  )
    self.job.log.info( 'driver id          = %s', self.driver_id       )
    self.job.log.info( 'kernel id          = %s', self.kernel_id       )

    if ( self.driver_version != share.version.VERSION ) :
      raise Exception()
    if ( self.driver_id      != 'block'               ) :
      raise Exception()

    self.kernel_sizeof_k = int( self.job.board.interact( '?reg k' ), 16 )
    self.kernel_sizeof_r = int( self.job.board.interact( '?reg r' ), 16 )
    self.kernel_sizeof_m = int( self.job.board.interact( '?reg m' ), 16 )
    self.kernel_sizeof_c = int( self.job.board.interact( '?reg c' ), 16 )

    self.job.log.info( 'kernel sizeof( k ) = %s', self.kernel_sizeof_k )
    self.job.log.info( 'kernel sizeof( r ) = %s', self.kernel_sizeof_r )
    self.job.log.info( 'kernel sizeof( m ) = %s', self.kernel_sizeof_m )
    self.job.log.info( 'kernel sizeof( c ) = %s', self.kernel_sizeof_c )

    self.kernel_k        = bytes( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_k ) ] )
