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
from sca3s.backend.acquire import kernel as kernel

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import abc

class DriverAbs( abc.ABC ) :
  def __init__( self, job ) :
    self.job         = job

    self.driver_id   = self.job.conf.get( 'driver_id'   )
    self.driver_spec = self.job.conf.get( 'driver_spec' )

  def _measure( self, trigger ) :
    edge_pos = sca3s_be.share.util.measure( sca3s_be.share.util.MEASURE_MODE_TRIGGER_POS, trigger, self.job.scope.channel_trigger_threshold )
    edge_neg = sca3s_be.share.util.measure( sca3s_be.share.util.MEASURE_MODE_TRIGGER_NEG, trigger, self.job.scope.channel_trigger_threshold )
      
    return ( edge_pos, edge_neg, float( edge_neg - edge_pos ) * self.job.scope.signal_interval )

  def _acquire_log_inc( self, i, n, message = None ) :
    width = len( str( n - 1 ) ) ; message = '' if ( message == None ) else ( ' : ' + message )
    self.job.log.indent_inc( message = 'started  acquiring trace {0:>{width}d} of {1:d} {message:s}'.format( i, n, width = width, message = message  ) )

  def _acquire_log_dec( self, i, n, message = None ) :
    width = len( str( n - 1 ) ) ; message = '' if ( message == None ) else ( ' : ' + message )
    self.job.log.indent_dec( message = 'finished acquiring trace {0:>{width}d} of {1:d} {message:s}'.format( i, n, width = width, message = message  ) )

  @abc.abstractmethod
  def acquire( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def prepare( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def execute_prologue( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def execute( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def execute_epilogue( self ) :
    raise NotImplementedError()
