# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

import sca3s_backend as be
import sca3s_spec    as spec

from sca3s_backend.acquire import board  as board
from sca3s_backend.acquire import scope  as scope
from sca3s_backend.acquire import driver as driver

from sca3s_backend.acquire import repo   as repo
from sca3s_backend.acquire import depo   as depo

import abc

class DriverAbs( abc.ABC ) :
  def __init__( self, job ) :
    super().__init__()  

    self.job         = job

    self.driver_id   = self.job.conf.get( 'driver-id'   )
    self.driver_spec = self.job.conf.get( 'driver-spec' )

  def calibrate( self, resolution = 8, dtype = '<f8' ) :
    l = be.share.sys.conf.get( 'timeout', section = 'job' )

    t = self.job.scope.calibrate( scope.CALIBRATE_MODE_DURATION, 1 * l, resolution = resolution, dtype = dtype )

    self.job.log.info( 'auto-calibration step #1, conf = %s', t )

    trace = self.acquire() ; l = be.share.util.measure( be.share.util.MEASURE_MODE_DURATION, trace[ 'trace/trigger' ], self.job.scope.channel_trigger_threshold ) * self.job.scope.signal_interval
    t = self.job.scope.calibrate( scope.CALIBRATE_MODE_DURATION, 2 * l, resolution = resolution, dtype = dtype )

    self.job.log.info( 'auto-calibration step #2, conf = %s', t )

    trace = self.acquire() ; l = be.share.util.measure( be.share.util.MEASURE_MODE_DURATION, trace[ 'trace/trigger' ], self.job.scope.channel_trigger_threshold ) * self.job.scope.signal_interval
    t = self.job.scope.calibrate( scope.CALIBRATE_MODE_DURATION, 1 * l, resolution = resolution, dtype = dtype )

    self.job.log.info( 'auto-calibration step #3, conf = %s', t )

    return t

  @abc.abstractmethod
  def prepare( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def acquire( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def execute( self ) :
    raise NotImplementedError()
