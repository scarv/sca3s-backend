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

import abc

class DriverAbs( abc.ABC ) :
  def __init__( self, job ) :
    self.job         = job

    self.driver_id   = self.job.conf.get( 'driver_id'   )
    self.driver_spec = self.job.conf.get( 'driver_spec' )

  def _measure( self, trigger ) :
    edge_lo = sca3s_be.share.util.measure( sca3s_be.share.util.MEASURE_MODE_TRIGGER_POS, trigger, self.job.scope.channel_trigger_threshold )
    edge_hi = sca3s_be.share.util.measure( sca3s_be.share.util.MEASURE_MODE_TRIGGER_NEG, trigger, self.job.scope.channel_trigger_threshold )
      
    return ( edge_hi, edge_lo, float( edge_hi - edge_lo ) * self.job.scope.signal_interval )

  def calibrate( self, resolution = 8, dtype = '<f8' ) :
    l = sca3s_be.share.sys.conf.get( 'timeout', section = 'job' )

    t = self.job.scope.calibrate( self.job.board, scope.CALIBRATE_MODE_DURATION, 1 * l, resolution = resolution, dtype = dtype )

    self.job.log.info( 'auto-calibration step #1, conf = %s', t )

    trace = self.acquire() ; l = sca3s_be.share.util.measure( sca3s_be.share.util.MEASURE_MODE_DURATION, trace[ 'trace/trigger' ], self.job.scope.channel_trigger_threshold ) * self.job.scope.signal_interval
    t = self.job.scope.calibrate( self.job.board, scope.CALIBRATE_MODE_DURATION, 2 * l, resolution = resolution, dtype = dtype )

    self.job.log.info( 'auto-calibration step #2, conf = %s', t )

    trace = self.acquire() ; l = sca3s_be.share.util.measure( sca3s_be.share.util.MEASURE_MODE_DURATION, trace[ 'trace/trigger' ], self.job.scope.channel_trigger_threshold ) * self.job.scope.signal_interval
    t = self.job.scope.calibrate( self.job.board, scope.CALIBRATE_MODE_DURATION, 1 * l, resolution = resolution, dtype = dtype )

    self.job.log.info( 'auto-calibration step #3, conf = %s', t )

    return t

  @abc.abstractmethod
  def acquire( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def prepare( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def process( self ) :
    raise NotImplementedError()
