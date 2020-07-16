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

import os

class BoardImp( board.scale.BoardType ) :
  def __init__( self, job ) :
    super().__init__( job )

  def get_channel_trigger_range( self ) :
    return   5.0E-0

  def get_channel_trigger_threshold( self ) :
    return   2.0E-0

  def get_channel_acquire_range( self ) :
    return 500.0E-3

  def get_channel_acquire_threshold( self ) :
    return None

  def get_build_context_vol( self ) :
    return {}

  def get_build_context_env( self ) :
    return {}

  def   program( self ) :  
    pass
