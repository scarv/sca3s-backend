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

import os, serial

class SCALE( board.BoardAbs ) :
  def __init__( self, job ) :
    super().__init__( job )
    
    self.connect_id      =      self.board_spec.get( 'connect-id'      )
    self.connect_timeout = int( self.board_spec.get( 'connect-timeout' ) )

    self.program_mode    =      self.board_spec.get( 'program-mode'    )
    self.program_id      =      self.board_spec.get( 'program-id'      )
    self.program_timeout = int( self.board_spec.get( 'program-timeout' ) )

  def _uart_send( self, x ) :
    self.board_object.write( ( x + '\x0D' ).encode() )

  def _uart_recv( self    ) :
    r = ''

    while( True ):
      t = self.board_object.read( 1 )

      if( t == '\x0D'.encode() ) :
        break
      else:
        r += ''.join( [ chr( x ) for x in t ] )

    return r

  def  open( self ) :
    self.board_object = serial.Serial( port = self.connect_id, timeout = self.connect_timeout, baudrate = 9600, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE )

    if ( self.board_object == None ) :
      raise Exception()

  def close( self ) :
    self.board_object.close()