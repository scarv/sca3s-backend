# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire        import share  as share

from acquire.device import board  as board
from acquire.device import scope  as scope
from acquire        import driver as driver

from acquire        import repo   as repo
from acquire        import depo   as depo

import abc

class BoardAbs( abc.ABC ) :
  def __init__( self, job ) :
    super().__init__()  

    self.job                       = job

    self.device                    = None
    self.device_id                 = self.job.conf.get( 'board-id'   )
    self.device_spec               = self.job.conf.get( 'board-spec' )

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

  @abc.abstractmethod
  def program( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def    open( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def   close( self ) :
    raise NotImplementedError()
