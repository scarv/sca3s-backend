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

CALIBRATE_MODE_INTERVAL  =    0
CALIBRATE_MODE_FREQUENCY =    1
CALIBRATE_MODE_DURATION  =    2

RESOLUTION_MIN           =    0
RESOLUTION_MAX           = 1024

ACQUIRE_MODE_PRIME       = 0x01
ACQUIRE_MODE_FETCH       = 0x02

class ScopeAbs( abc.ABC ) :
  def __init__( self, job ) :
    self.job                       = job

    self.scope_object              = None
    self.scope_id                  = self.job.conf.get( 'scope_id'   )
    self.scope_spec                = self.job.conf.get( 'scope_spec' )
    self.scope_mode                = self.job.conf.get( 'scope_mode' )
    self.scope_path                = self.job.conf.get( 'scope_path' )

    self.channel_trigger_range     = None
    self.channel_trigger_threshold = None
    self.channel_acquire_range     = None
    self.channel_acquire_threshold = None

    self.signal_interval           = None
    self.signal_duration           = None

    self.signal_resolution         = None
    self.signal_type               = None
    self.signal_length             = None

  @abc.abstractmethod
  def calibrate( self, x, mode = scope.CALIBRATE_MODE_DURATION, resolution = 8, dtype = '<f8' ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def   acquire( self,    mode = scope.ACQUIRE_MODE_PRIME | ACQUIRE_MODE_FETCH ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def      open( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def     close( self ) :
    raise NotImplementedError()
