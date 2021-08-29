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

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import math, picoscope.ps2000a as api

# PicoScope 2206B
# ---------------
# 
# specification     : using 1 segment, 2 (of 2) channels @ 8-bit resolution => 50 MHz, 250 MS/s, 16 MS per channel (32 MS total)
#
# datasheet         : https://www.picotech.com/download/datasheets/picoscope-2000-series-data-sheet-en.pdf
# programming guide : https://www.picotech.com/download/manuals/picoscope-2000-series-a-api-programmers-guide.pdf

class ScopeImp( scope.picoscope.ScopeType ) :
  def __init__( self, job ) :
    super().__init__( job, api.PS2000a )
    
  def _resolutions( self ) :
    return [ 8 ]

  def _maxSamples( self, resolution ) :
    if ( resolution ==  8 ) :
      return  16.0e6

  def _interval2timebase( self, resolution, x ) :
    if ( resolution ==  8 ) :
      if   ( x <   8.0e-9 ) :
        t = 1
      elif ( x <  16.0e-9 ) :
        t = math.log( x * 500.0e6, 2 )
      else :
        t = ( x *  62.5e6 ) + 2

    return round( t )

  def _timebase2interval( self, resolution, x ) :
    if ( resolution ==  8 ) :
      if   ( x <  2 ) :
        t = 4.0e-9
      elif ( x <  3 ) :
        t = math.pow( 2, x ) / 500.0e6
      else :
        t = ( x - 2 ) /  62.5e6

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
