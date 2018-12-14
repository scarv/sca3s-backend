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

from .              import *

import math, picoscope.ps2000a as api

PS2000A_RATIO_MODE_NONE      = 0 # Section 3.18.1
PS2000A_RATIO_MODE_AGGREGATE = 1 # Section 3.18.1
PS2000A_RATIO_MODE_DECIMATE  = 2 # Section 3.18.1
PS2000A_RATIO_MODE_AVERAGE   = 4 # Section 3.18.1

class ScopeImp( PicoScope ) :
  def __init__( self, job ) :
    super().__init__( job, api.PS2000a )

    schema = {
      'type' : 'object', 'default' : {}, 'properties' : {
                'connect-timeout' : { 'type' : 'number', 'default' : 10000     },
                'connect-id'      : { 'type' : 'string'                        },
        'channel-trigger-id'      : { 'type' : 'string', 'enum' : [ 'A', 'B' ] },
        'channel-acquire-id'      : { 'type' : 'string', 'enum' : [ 'A', 'B' ] }
      }
    }

    share.conf.validate( self.device_spec, schema )
    
    self.connect_id         = self.device_spec.get( 'connect-id'         )
    self.connect_timeout    = self.device_spec.get( 'connect-timeout'    )

    self.channel_trigger_id = self.device_spec.get( 'channel-trigger-id' )
    self.channel_acquire_id = self.device_spec.get( 'channel-acquire-id' )

  def _interval2timebase( self, x ) :
    # Section 2.8, Page 21: timebase selection
    if   ( x <  4E-9 ) :
      t = 1
    elif ( x < 16E-9 ) :
      t = math.log( x * 500E6, 2 )
    else :
      t = ( x * 625E5 ) + 2

    return round( t )

  def _timebase2interval( self, x ) :
    # Section 2.8, Page 21: timebase selection
    if   ( x < 0    ) :
      t = 0
    elif ( x < 3    ) :
      t = math.pow( 2, x ) / 500E6
    else :
      t = ( x - 2 ) / 625E5

    return        t

  def conf( self, mode, x ) :  
    if   ( mode == scope.CONF_MODE_INTERVAL  ) :
      interval =     x
      timebase = self._interval2timebase( interval )
      interval = self._timebase2interval( timebase ) ; duration =         interval * 16e6  
  
    elif ( mode == scope.CONF_MODE_FREQUENCY ) :
      interval = 1 / x
      timebase = self._interval2timebase( interval )
      interval = self._timebase2interval( timebase ) ; duration =         interval * 16e6  
  
    elif ( mode == scope.CONF_MODE_DURATION  ) :
      interval =     x / 16e6
      timebase = self._interval2timebase( interval )
      interval = self._timebase2interval( timebase ) ; duration = min( x, interval * 16e6 )

    self.signal_interval = interval
    self.signal_duration = duration

    return { 'timebase' : timebase, 'interval' : interval, 'duration' : duration }

  def acquire( self, mode ) :
    if ( self.device == None ) :
      raise Exception()

    if ( mode & scope.ACQUIRE_MODE_PREPARE ) :
      # Section 3.39, Page 69; Step  2: configure channels
      self.device.setChannel( channel = self.channel_trigger_id, enabled = True, coupling = 'DC', VRange = self.channel_trigger_range )
      self.device.setChannel( channel = 'B', enabled = True, coupling = 'DC', VRange = self.channel_acquire_range )
  
      # Section 3.13, Page 36; Step  3: configure timebase
      ( _, samples, samples_max ) = self.device.setSamplingInterval( self.signal_interval, self.signal_duration )

      # Section 3.56, Page 93; Step  4: configure trigger
      self.device.setSimpleTrigger( self.channel_trigger_id, threshold_V = self.channel_trigger_threshold, direction = 'Rising', timeout_ms = self.connect_timeout )
    
      # Section 3.37, Page 65; Step  5: start acquisition
      self.device.runBlock()

    if ( mode & scope.ACQUIRE_MODE_COLLECT ) :
      # Section 3.26, Page 54; Step  6: wait for acquisition to complete  
      self.device.waitReady()
    
      # Section 3.40, Page 71; Step  7: configure buffers
      # Section 3.18, Page 43; Step  8; transfer  buffers
      signal_trigger = self.device.getDataV( channel = self.channel_trigger_id, downSampleMode = PS2000A_RATIO_MODE_NONE )
      signal_acquire = self.device.getDataV( channel = self.channel_acquire_id, downSampleMode = PS2000A_RATIO_MODE_NONE )

      # Section 3.2,  Page 25; Step 10: stop  acquisition
      self.device.stop()

      return ( signal_trigger, signal_acquire )

    return None
