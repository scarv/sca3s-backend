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

import binascii, h5py, numpy

class DriverImp( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

  def hdf5_add_attr( self, fd              ) :
    pass

  def hdf5_add_data( self, fd, n           ) :
    pass

  def hdf5_set_data( self, fd, n, i, trace ) :
    pass

  def prepare( self ) : 
    if ( not sca3s_be.share.version.match( self.job.board.driver_version ) ) :
      raise Exception( 'inconsistent driver version'    )
    if ( self.driver_id !=               ( self.job.board.driver_id      ) ) :
      raise Exception( 'inconsistent driver identifier' )
    
    if ( self.job.board.kernel.nameof not in [ 'generic' ] ) :
      raise Exception( 'unsupported kernel name'   )
    if ( self.job.board.kernel.modeof not in [ 'default' ] ) :
      raise Exception( 'unsupported kernel type'   )

    if ( self.job.board.kernel.modeof == 'default' ) :
      if ( not ( self.job.board.kernel.data_wr_id <= set( [        'esr', 'x0', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )
      if ( not ( self.job.board.kernel.data_rd_id <= set( [ 'fec', 'fcc', 'r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )

    if ( ( self.policy_id == 'user' ) and not self.job.board.kernel.supports_policy_user( self.policy_spec ) ) :
      raise Exception( 'unsupported kernel policy' )
    if ( ( self.policy_id == 'tvla' ) and not self.job.board.kernel.supports_policy_tvla( self.policy_spec ) ) :
      raise Exception( 'unsupported kernel policy' )
