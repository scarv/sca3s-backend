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

import os, serial, more_itertools as mit

class SCALE( board.BoardAbs ) :
  def __init__( self, job ) :
    super().__init__( job )
    
    self.connect_id      =      self.board_spec.get( 'connect-id'      )
    self.connect_timeout = int( self.board_spec.get( 'connect-timeout' ) )

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

  def program( self ) :  
    env = { 'REPO_HOME' : os.path.join( self.job.path, 'target' ), 'BOARD' : self.job.conf.get( 'board-id' ), 'TARGET' : mit.first( self.job.conf.get( 'driver-id' ).split( '/' ) ), 'CONF' : ' '.join( [ '-D' + str( k ) + '=' + '"' + str( v ) + '"' for ( k, v ) in self.job.repo.conf.items() ] ), 'CACHE' : share.sys.conf.get( 'git', section = 'path' ), 'USB' : self.connect_id }

    self.job.extern( [ 'make', '-C', 'target', '--no-builtin-rules', 'deps-fetch' ], env = env )
    self.job.extern( [ 'make', '-C', 'target', '--no-builtin-rules', 'deps-build' ], env = env )

    self.job.extern( [ 'make', '-C', 'target', '--no-builtin-rules',      'build' ], env = env )
    self.job.extern( [ 'make', '-C', 'target', '--no-builtin-rules',     'report' ], env = env )

    self.job.extern( [ 'make', '-C', 'target', '--no-builtin-rules',    'program' ], env = env, timeout = self.program_timeout )

    self.job.extern( [ 'make', '-C', 'target', '--no-builtin-rules',      'clean' ], env = env )

  def    open( self ) :
    self.board_object = serial.Serial( port = self.connect_id, timeout = self.connect_timeout, baudrate = 9600, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE )

    if ( self.board_object == None ) :
      raise Exception()

  def   close( self ) :
    self.board_object.close()
