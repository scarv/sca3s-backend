# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import os

class BoardImp( board.scale.BoardType ) :
  def __init__( self, job ) :
    super().__init__( job )

  def get_channel_trigger_range( self ) :
    return   5.0E-0

  def get_channel_trigger_threshold( self ) :
    return   2.0E-0

  def get_channel_acquire_range( self ) :
    return 500.0E-3

  def get_channel_acquire_threshold( self ) :
    return None

  def get_build_context_vol( self ) :
    return {}

  def get_build_context_env( self ) :
    return { 'JLINK' : self.program_id }

  def   program( self ) :  
    target = os.path.join( self.job.path, 'target', 'build', self.board_id, 'target.hex' )

    if ( not os.path.isfile( target ) ) :
      raise Exception( 'failed to open target program' )

    if   ( self.program_mode == 'usb'   ) :
      cmd = [ 'lpc21isp', '-wipe', target, self.program_id, '9600', '12000' ]
    elif ( self.program_mode == 'jlink' ) :
      cmd = [ 'openocd', '--file', 'interface/jlink.cfg', '--command', 'jlink serial %s' % ( self.program_id ), '--command', 'transport select swd', '--file', 'target/lpc13xx.cfg', '--command', 'init', '--command', 'reset init', '--command', 'flash write_image erase %s' % ( target ), '--command', 'reset run', '--command', 'shutdown' ]
    else :
      raise Exception( 'unknown programming mode' )

    self.job.exec_native( cmd, env = { 'PATH' : os.pathsep.join( self.board_path ) + os.pathsep + os.environ[ 'PATH' ] }, timeout = self.program_timeout )
