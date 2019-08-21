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

from .                     import *

import math, picoscope.ps3000a as api

# PicoScope 3406B
# ---------------
# 
# specification     : using 1 segment, 2 (of 4) channels @ 8-bit resolution => 200 MHz, 500 MS/s, 64 MS per channel (128 MS total)
#
# datasheet         : https://www.picotech.com/download/datasheets/PicoScope3400.pdf
# programming guide : https://www.picotech.com/download/manuals/picoscope-3000-series-a-api-programmers-guide.pdf

class ScopeImp( PicoScope ) :
  def __init__( self, job ) :
    super().__init__( job, api.PS3000a )    

  def _interval2timebase( self, x ) :
    if   ( x <   4.0e-9 ) :
      t = 1
    elif ( x <   8.0e-9 ) :
      t = math.log( x *   1.0e9, 2 )
    else :
      t = ( x * 125.0e6 ) + 2

    return round( t )

  def _timebase2interval( self, x ) :
    if   ( x <  2 ) :
      t = 2.0e-9
    elif ( x <  3 ) :
      t = math.pow( 2, x ) /   1.0e9
    else :
      t = ( x - 2 ) / 125.0e6

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

  def conf( self, mode, x, resolution = None ) :    
    maxSamples = 64.0e6

    if   ( mode == scope.CONF_MODE_INTERVAL  ) :
      interval =     x
      timebase = self._interval2timebase( interval )
      interval = self._timebase2interval( timebase ) ; duration =         interval * maxSamples  
  
    elif ( mode == scope.CONF_MODE_FREQUENCY ) :
      interval = 1 / x
      timebase = self._interval2timebase( interval )
      interval = self._timebase2interval( timebase ) ; duration =         interval * maxSamples  
  
    elif ( mode == scope.CONF_MODE_DURATION  ) :
      interval =     x / maxSamples
      timebase = self._interval2timebase( interval )
      interval = self._timebase2interval( timebase ) ; duration = min( x, interval * maxSamples )

    self.signal_resolution = 8
    self.signal_interval   = interval
    self.signal_duration   = duration

    return { 'resolution' : self.signal_resolution, 'interval' : self.signal_interval, 'duration' : self.signal_duration }
