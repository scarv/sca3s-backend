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

class ScopeImp( scope.joulescope.ScopeType ) :
  def __init__( self, job ) :
    super().__init__( job )

  def calibrate( self, mode = scope.CALIBRATE_MODE_DEFAULT, value = None, resolution = 8, dtype = '<f8' ) :  
    pass

  def acquire( self, mode = scope.ACQUIRE_MODE_PRIME | scope.ACQUIRE_MODE_FETCH ) :
    pass

  def  open( self ) :
    pass

  def close( self ) :
    pass
