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

from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import os

class BoardType( board.BoardAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.uart_id            =      self.board_spec.get(       'uart_id'      )
    self.uart_timeout       = int( self.board_spec.get(       'uart_timeout' )     )
    self.uart_mode          =      self.board_spec.get(       'uart_mode'    )

    self.program_sw_id      =      self.board_spec.get( 'program_sw_id'      )
    self.program_sw_timeout = int( self.board_spec.get( 'program_sw_timeout' )     )
    self.program_sw_mode    =      self.board_spec.get( 'program_sw_mode'    )
    self.program_sw_addr    = int( self.board_spec.get( 'program_sw_addr'    ), 16 )

    self.program_hw_id      =      self.board_spec.get( 'program_hw_id'      )
    self.program_hw_timeout = int( self.board_spec.get( 'program_hw_timeout' )     )
    self.program_hw_mode    =      self.board_spec.get( 'program_hw_mode'    )

  def get_channel_trigger_range( self ) :
    return   5.0e-0

  def get_channel_trigger_threshold( self ) :
    return   2.0e-0

  def get_channel_acquire_range( self ) :
    return 100.0e-3

  def get_channel_acquire_threshold( self ) :
    return None

  def get_docker_vol ( self ) :
    return {}

  def get_docker_env ( self ) :
    return {}

  def get_docker_conf( self ) :
    return []

  def  open( self ) :
    self.board_uart = self.uart_open( self.uart_id, self.uart_timeout, self.uart_mode )

    if ( self.board_uart == None ) :
      raise Exception( 'failed to open board' )

  def close( self ) :
    if ( self.board_uart != None ) :
      self.board_uart.close()
