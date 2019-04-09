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

  def _process_prologue( self ) : 
    t = self.job.board.interact( '?id' ).split( ':' )

    if ( len( t ) != 2 ) :
      raise Exception()

    self.driver_type    = t[ 0 ]
    self.driver_version = t[ 1 ]

    if ( self.driver_type    != 'block'               ) :
      raise Exception()
    if ( self.driver_version != share.version.VERSION ) :
      raise Exception()

    self.kernel_sizeof_k = int( self.job.board.interact( '?reg k' ), 16 )
    self.kernel_sizeof_r = int( self.job.board.interact( '?reg r' ), 16 )
    self.kernel_sizeof_m = int( self.job.board.interact( '?reg m' ), 16 )
    self.kernel_sizeof_c = int( self.job.board.interact( '?reg c' ), 16 )

    self.kernel_k        = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_k ) ] )

    self.job.log.info( 'driver type        = %s', self.driver_type     )
    self.job.log.info( 'driver version     = %s', self.driver_version  )

    self.job.log.info( 'driver sizeof( k ) = %s', self.kernel_sizeof_k )
    self.job.log.info( 'driver sizeof( r ) = %s', self.kernel_sizeof_r )
    self.job.log.info( 'driver sizeof( m ) = %s', self.kernel_sizeof_m )
    self.job.log.info( 'driver sizeof( c ) = %s', self.kernel_sizeof_c )

  def _process_epilogue( self ) : 
    pass
