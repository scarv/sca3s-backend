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
from sca3s.backend.acquire import kernel as kernel

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import binascii, h5py, importlib, numpy, os

class DriverImp( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

  # Acquire data wrt. this driver

  def acquire( self, x = None ) :
    pass

  # Prepare the driver

  def prepare( self ) : 
    pass

  # Execute the driver prologue

  def execute_prologue( self ) :
    pass

  # Execute the driver

  def execute( self ) :
    pass

  # Execute the driver epilogue

  def execute_epilogue( self ) :
    pass
