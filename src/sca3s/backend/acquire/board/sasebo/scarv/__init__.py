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

  def program_hw( self ) :  
    fn_tcl = os.path.join( self.job.path, 'target', 'src', 'sca3s', 'harness', 'board', self.board_id, 'fpga.tcl' )
    fn_bit = os.path.join( self.job.path, 'target', 'src', 'sca3s', 'harness', 'board', self.board_id, 'fpga.bit' )

    if ( not os.path.isfile( fn_tcl ) ) :
      raise Exception( 'failed to open file' )
    if ( not os.path.isfile( fn_bit ) ) :
      raise Exception( 'failed to open file' )

    if   ( self.program_hw_mode == 'jtag' ) :
      cmd = [ 'vivado', '-mode', 'tcl', '-nolog', '-nojournal', '-source', fn_tcl, '-tclargs', self.program_hw_id, fn_bit ]
    else :
      raise Exception( 'unsupported programming mode' )

    self.job.exec_native( cmd, env = { 'PATH' : os.pathsep.join( self.board_path ) + os.pathsep + os.environ[ 'PATH' ] }, timeout = self.program_hw_timeout )

  def program_sw( self ) :  
    fn_bin = os.path.join( self.job.path, 'target', 'build', self.board_id, 'target.bin' )

    if ( not os.path.isfile( fn_bin ) ) :
      raise Exception( 'failed to open file' )

    if   ( self.program_sw_mode == 'uart' ) :
      with open( fn_bin, 'rb' ) as fd_bin:
        self.job.log.info( 'reading FSBL prompt' )

        if ( str( self.board_uart.readline(), encoding = 'ascii' ) != 'scarv-soc fsbl\n' ) :
          raise Exception( 'cannot parse FSBL prompt' )

        data = fd_bin.read() ; size = len( data ) ; addr = self.program_sw_addr

        size = size.to_bytes( 4, byteorder='little' )
        addr = addr.to_bytes( 4, byteorder='little' )
  
        self.job.log.info( 'writing size    (%d bytes)', len( size ) )
        self.board_uart.write( size[::-1] )
        self.job.log.info( 'writing address (%d bytes)', len( addr ) )
        self.board_uart.write( addr[::-1] )
        self.job.log.info( 'writing data    (%d bytes)', len( data ) )
        self.board_uart.write( data       )
  
        self.board_uart.flush()

    else :
      raise Exception( 'unsupported programming mode' )

  def  open( self ) :
    self.board_uart = self.uart_open( self.uart_id, self.uart_timeout, self.uart_mode )

    if ( self.board_uart == None ) :
      raise Exception( 'failed to open board' )

  def close( self ) :
    if ( self.board_uart != None ) :
      self.board_uart.close()
