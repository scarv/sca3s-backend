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

import math, picoscope.ps5000a as api

# PicoScope 5444B
# ---------------
# 
# specification     : using 2 (of 4) channels @  8-bit resolution => 200 MHz, 500 GS/s, 256 MS buffer (512 MS total)
#                                             @ 12-bit resolution => 200 MHz, 250 GS/s, 128 MS buffer (256 MS total)
#                                             @ 14-bit resolution => 200 MHz, 125 GS/s, 128 MS buffer (256 MS total)
#                                             @ 15-bit resolution => 200 MHz, 125 GS/s, 128 MS buffer (256 MS total)
#
# datasheet         : https://www.picotech.com/download/datasheets/picoscope-5000-series-a-b-data-sheet.pdf
# programming guide : https://www.picotech.com/download/manuals/picoscope-5000-series-a-api-programmers-guide.pdf

class ScopeImp( PicoScope ) :
  def __init__( self, job ) :
    super().__init__( job, api.PS5000a )
    
    self.connect_id         = self.device_spec.get( 'connect-id'         )
    self.connect_timeout    = self.device_spec.get( 'connect-timeout'    )

    self.channel_trigger_id = self.device_spec.get( 'channel-trigger-id' )
    self.channel_acquire_id = self.device_spec.get( 'channel-acquire-id' )

  def _interval2timebase( self, x, resolution ) :
    if   ( resolution ==  8 ) :
      if   ( x <   2.0e-9 ) :
        t = 1
      elif ( x <   8.0e-9 ) :
        t = math.log( ( x - 0 ) *   1.0e9, 2 )
      else :
        t = ( x * 125.0e6 ) + 2

    elif ( resolution == 12 ) :
      if   ( x <   4.0e-9 ) :
        t = 2
      elif ( x <  16.0e-9 ) :
        t = math.log( ( x - 1 ) * 500.0e6, 2 )
      else :
        t = ( x *  62.5e6 ) + 3

    elif ( resolution == 14 ) :
      if   ( x <   8.0e-9 ) :
        t = 3
      elif ( x <  16.0e-9 ) :
        t = 1 / 125.0e6
      else :
        t = ( x * 125.0e6 ) + 2

    elif ( resolution == 15 ) :
      if   ( x <   8.0e-9 ) :
        t = 3
      elif ( x <  16.0e-9 ) :
        t = 1 / 125.0e6
      else :
        t = ( x * 125.0e6 ) + 2

    return round( t )

  def _timebase2interval( self, x, resolution ) :
    if   ( resolution ==  8 ) :
    elif ( resolution == 12 ) :
    elif ( resolution == 14 ) :
    elif ( resolution == 15 ) :

    return        t

  def _downSampleMode( self, x ) :
    if   ( x == PICOSCOPE_DOWNSAMPLE_MODE_NONE      ) :
      return 0
    elif ( x == PICOSCOPE_DOWNSAMPLE_MODE_AGGREGATE ) :
      return 1
    elif ( x == PICOSCOPE_DOWNSAMPLE_MODE_DECIMATE  ) :
      return 2
    elif ( x == PICOSCOPE_DOWNSAMPLE_MODE_AVERAGE   ) :
      return 4

  def conf( self, mode, x, resolution ) :  
    resolution = share.util.closest( resolution, [ 8, 12, 14, 15, 16 ] )

    if   ( mode == scope.CONF_MODE_INTERVAL  ) :
      interval =     x
      timebase = self._interval2timebase( interval, resolution )
      interval = self._timebase2interval( timebase, resolution ) ; duration =         interval * 16e6  
  
    elif ( mode == scope.CONF_MODE_FREQUENCY ) :
      interval = 1 / x
      timebase = self._interval2timebase( interval, resolution )
      interval = self._timebase2interval( timebase, resolution ) ; duration =         interval * 16e6  
  
    elif ( mode == scope.CONF_MODE_DURATION  ) :
      interval =     x / 16e6
      timebase = self._interval2timebase( interval, resolution )
      interval = self._timebase2interval( timebase, resolution ) ; duration = min( x, interval * 16e6 )

    self.signal_resolution = resolution
    self.signal_interval   = interval
    self.signal_duration   = duration

    return { 'resolution' : self.signal_resolution, 'interval' : self.signal_interval, 'duration' : self.signal_duration }
