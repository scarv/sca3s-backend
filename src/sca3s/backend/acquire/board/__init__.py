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

import abc, os, struct

class BoardAbs( abc.ABC ) :
  def __init__( self, job ) :
    self.job                       = job

    self.board_object              = None
    self.board_id                  = self.job.conf.get( 'board_id'   )
    self.board_spec                = self.job.conf.get( 'board_spec' )
    self.board_mode                = self.job.conf.get( 'board_mode' )
    self.board_path                = self.job.conf.get( 'board_path' )

    self.driver_version            = None
    self.driver_id                 = None

    self.kernel_id                 = None
    self.kernel_io                 = dict()

  @abc.abstractmethod
  def get_channel_trigger_range( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def get_channel_trigger_threshold( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def get_channel_acquire_range( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def get_channel_acquire_threshold( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def get_build_context_vol( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def get_build_context_env( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def uart_send( self, x ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def uart_recv( self    ) :
    raise NotImplementedError()

  def  interact( self, x ) :
    sca3s_be.share.sys.log.debug( '> uart : %s', x )
    self.uart_send( x ) ; t = self.uart_recv()
    sca3s_be.share.sys.log.debug( '< uart : %s', t )

    if   ( t[ 0 ] == '+' ) :
      return t[ 1 : ]
    elif ( t[ 0 ] == '-' ) :
      raise Exception( 'board interaction failed => ack=-' )
    elif ( t[ 0 ] == '~' ) :
      raise Exception( 'board interaction failed => ack=~' )
    else :
      raise Exception( 'board interaction failed => ack=?' )

  def        io( self ) :
    fn = os.path.join( self.job.path, 'target', 'build', self.board_id, 'target.io' )

    if ( not os.path.isfile( fn ) ) :
      raise Exception( 'failed to open %s' % ( fn ) )

    fd = open( fn, 'r' )

    for line in fd.readlines() :
      t = line.split( '=' ) 

      if ( len( t ) != 2 ) :
        continue

      k = t[ 0 ].strip()
      v = t[ 1 ].strip()
        
      self.kernel_io[ k ] = v

    # produce dummy data for each potential input and output

    def f( x ) :
      if ( x in self.kernel_io ) :
        for id in self.kernel_io[ x ].split( ',' ) :
          if ( ( '?data %s' % ( id ) ) in self.kernel_io ) :
            n = int( self.kernel_io[ '?data %s' % ( id ) ] )

            self.kernel_io[ '>data %s' % ( id ) ] = sca3s_be.share.util.str2octetstr( bytes( [ 0 ] * n ) )
            self.kernel_io[ '<data %s' % ( id ) ] = sca3s_be.share.util.str2octetstr( bytes( [ 0 ] * n ) )

    f( '?kernel_data <' )
    f( '?kernel_data >' )

    # convert integer sizes into octet strings

    for ( k, v ) in self.kernel_io.items() :
      if ( k.startswith( '?data' ) ) :
        self.kernel_io[ k ] = sca3s_be.share.util.str2octetstr( struct.pack( '<I', int( v ) ) )

    for ( k, v ) in self.kernel_io.items() :
      self.job.log.info( 'parsed non-interactive I/O response: %s => %s' % ( k, v ) )

    fd.close()

  def   prepare( self ) :
    t = self.interact( '?kernel_id' ).split( ':' )
  
    if ( len( t ) != 3 ) :
      raise Exception( 'unparsable kernel identifier' )
  
    self.driver_version = t[ 0 ]
    self.driver_id      = t[ 1 ]
  
    self.kernel_id      = t[ 2 ]
  
    self.job.log.info( '?kernel_id   -> driver version     = %s', self.driver_version )
    self.job.log.info( '?kernel_id   -> driver id          = %s', self.driver_id      )
    self.job.log.info( '?kernel_id   -> kernel id          = %s', self.kernel_id      )
  
    self.kernel_data_i = set( self.job.board.interact( '?kernel_data <' ).split( ',' ) )
    self.kernel_data_o = set( self.job.board.interact( '?kernel_data >' ).split( ',' ) )
  
    self.job.log.info( '?kernel_data -> kernel data  input = %s', self.kernel_data_i  )
    self.job.log.info( '?kernel_data -> kernel data output = %s', self.kernel_data_o  )

  @abc.abstractmethod
  def   program( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def      open( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def     close( self ) :
    raise NotImplementedError()
