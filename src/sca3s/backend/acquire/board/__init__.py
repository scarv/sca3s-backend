# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend as be
from sca3s import spec    as spec

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import abc

class BoardAbs( abc.ABC ) :
  def __init__( self, job ) :
    super().__init__()  

    self.job            = job

    self.board_object   = None
    self.board_id       = self.job.conf.get( 'board-id'   )
    self.board_spec     = self.job.conf.get( 'board-spec' )

    self.driver_version = None
    self.driver_id      = None
    self.kernel_id      = None

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
  def _uart_send( self, x ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def _uart_recv( self    ) :
    raise NotImplementedError()

  def interact( self, x ) :
    self.job.log.debug( '> uart : %s', x )
    self._uart_send( x ) ; t = self._uart_recv()
    self.job.log.debug( '< uart : %s', t )

    if   ( t[ 0 ] == '+' ) :
      return t[ 1 : ]
    elif ( t[ 0 ] == '-' ) :
      raise Exception()
    elif ( t[ 0 ] == '~' ) :
      raise Exception()
    else :
      raise Exception()

  def prepare( self ) :
    t = self.interact( '?id' ).split( ':' )

    if ( len( t ) != 3 ) :
      raise Exception()

    self.driver_version = t[ 0 ]
    self.driver_id      = t[ 1 ]
    self.kernel_id      = t[ 2 ]

    if ( self.driver_version != be.share.version.VERSION ) :
      raise Exception()

    self.job.log.info( '?id -> driver version = %s', self.driver_version )
    self.job.log.info( '?id -> driver id      = %s', self.driver_id      )
    self.job.log.info( '?id -> kernel id      = %s', self.kernel_id      )

  @abc.abstractmethod
  def program( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def  open( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def close( self ) :
    raise NotImplementedError()
