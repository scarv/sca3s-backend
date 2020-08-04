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

from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

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

class ScopeImp( scope.picoscope.ScopeType ) :
  def __init__( self, job ) :
    super().__init__( job, api.PS5000a )

  def _resolutions( self ) :
    return [ 8, 12, 14, 15 ]

  def _maxSamples( self, resolution ) :
    if   ( resolution ==  8 ) :
      return 256.0e6
    elif ( resolution == 12 ) :
      return 128.0e6
    elif ( resolution == 14 ) :
      return 128.0e6
    elif ( resolution == 15 ) :
      return 128.0e6

  def _interval2timebase( self, resolution, x ) :
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

  def _timebase2interval( self, resolution, x ) :
    if   ( resolution ==  8 ) :
    elif ( resolution == 12 ) :
    elif ( resolution == 14 ) :
    elif ( resolution == 15 ) :

    return        t

  def _downSampleMode( self, x ) :
    if   ( x == scope.picoscope.PICOSCOPE_DOWNSAMPLE_MODE_NONE      ) :
      return 0
    elif ( x == scope.picoscope.PICOSCOPE_DOWNSAMPLE_MODE_AGGREGATE ) :
      return 1
    elif ( x == scope.picoscope.PICOSCOPE_DOWNSAMPLE_MODE_DECIMATE  ) :
      return 2
    elif ( x == scope.picoscope.PICOSCOPE_DOWNSAMPLE_MODE_AVERAGE   ) :
      return 4
