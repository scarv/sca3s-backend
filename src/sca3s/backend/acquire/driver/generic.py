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

import binascii, h5py, importlib, numpy, os

class DriverImp( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.trace_spec    = self.job.conf.get( 'trace_spec' )

    self.trace_content =       self.trace_spec.get( 'content' )
    self.trace_count   =  int( self.trace_spec.get( 'count'   ) )

  # Acquire data wrt. this driver, using the kernel model.

  def acquire( self, k = None, x = None ) :
    pass

  # Prepare the driver:
  #
  # 1. check the on-board driver
  # 2. query the on-board kernel
  # 3. build a model of the on-board kernel
  # 4. check the model supports whatever policy is selected

  def prepare( self ) : 
    if ( self.job.board.driver_version != sca3s_be.share.version.VERSION ) :
      raise Exception( 'mismatched driver version'    )
    if ( self.job.board.driver_id      != 'generic'                      ) :
      raise Exception( 'mismatched driver identifier' )

  # Process the driver:
  #
  # 1. open     HDF5 file
  # 2. execute selected policy
  # 3. close    HDF5 file
  # 4. compress HDF5 file

  def process( self ) :
    fd = h5py.File( os.path.join( self.job.path, 'acquire.hdf5' ), 'a' )

    fd.close()

    self.job.exec_native( [ 'gzip', '--quiet', os.path.join( self.job.path, 'acquire.hdf5' ) ] )
