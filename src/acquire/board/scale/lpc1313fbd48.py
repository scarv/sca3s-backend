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

class BoardImp( SCALE ) :
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

  def program( self ) :  
    target = os.path.join( self.job.path, 'target', 'build', 'target.hex' )

    if ( not os.path.isfile( target ) ) :
      raise Exception()

    if   ( self.program_mode == 'usb'   ) :
      cmd = [ 'lpc21isp', '-wipe', target, self.program_id, '9600', '12000' ]
    elif ( self.program_mode == 'jlink' ) :
      cmd = [ 'openocd', '--file', 'interface/jlink.cfg', '--command', 'jlink serial %s' % ( self.program_id ), '--command', 'transport select swd', '--file', 'target/lpc13xx.cfg', '--command', 'init', '--command', 'reset init', '--command', 'flash write_image erase %s' % ( target ), '--command', 'reset run', '--command', 'shutdown' ]
    else :
      raise Exception()

    self.job.run( cmd, timeout = self.program_timeout )
