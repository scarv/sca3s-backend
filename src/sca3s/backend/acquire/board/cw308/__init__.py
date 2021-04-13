# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import hybrid as hybrid

from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

class BoardType( board.BoardAbs ) :
  def __init__( self, job ) :
    super().__init__( job )
    
    self.uart_id            =      self.board_spec.get(       'uart_id'      )
    self.uart_timeout       = int( self.board_spec.get(       'uart_timeout' ) )
    self.uart_mode          =      self.board_spec.get(       'uart_mode'    )

    self.program_sw_id      =      self.board_spec.get( 'program_sw_id'      )
    self.program_sw_timeout = int( self.board_spec.get( 'program_sw_timeout' ) )
    self.program_sw_mode    =      self.board_spec.get( 'program_sw_mode'    )

  def  open( self ) :
    self.board_uart = self.uart_open( self.uart_id, self.uart_timeout, self.uart_mode )

    if ( self.board_uart == None ) :
      raise Exception( 'failed to open board' )

  def close( self ) :
    if ( self.board_uart != None ) :
      self.board_uart.close()
