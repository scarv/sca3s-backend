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

import abc

CONF_MODE_INTERVAL    = 0
CONF_MODE_FREQUENCY   = 1
CONF_MODE_DURATION    = 2

ACQUIRE_MODE_PREPARE  = 0b01
ACQUIRE_MODE_COLLECT  = 0b10

class ScopeAbs( abc.ABC ) :
  def __init__( self, job ) :
    super().__init__()  

    self.job                       = job

    self.scope_object              = None
    self.scope_id                  = self.job.conf.get( 'scope-id'   )
    self.scope_spec                = self.job.conf.get( 'scope-spec' )

    self.channel_trigger_range     = None
    self.channel_trigger_threshold = None
    self.channel_acquire_range     = None
    self.channel_acquire_threshold = None

    self.signal_resolution         = None
    self.signal_interval           = None
    self.signal_duration           = None

  @abc.abstractmethod
  def  open( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def close( self ) :
    raise NotImplementedError()
