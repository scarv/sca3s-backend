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

class DriverType( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

  def prepare( self ) :     
    if ( self.job.board.kernel_id_nameof not in [ 'generic', 'aes' ] ) :
      raise Exception( 'unsupported kernel name' )
    if ( self.job.board.kernel_id_modeof not in [ 'default', 'enc', 'dec' ] ) :
      raise Exception( 'unsupported kernel type' )

    if   ( self.job.board.kernel_id_modeof == 'default' ) :
      self.job.board.kernel_id_modeof = 'enc'

    if   ( self.job.board.kernel_id_modeof == 'enc'     ) :
      if ( not ( self.job.board.kernel_data_wr_id == set( [        'esr', 'k', 'm' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )
      if ( not ( self.job.board.kernel_data_rd_id == set( [ 'fec', 'fcc',      'c' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )
    elif ( self.job.board.kernel_id_modeof == 'dec'     ) :
      if ( not ( self.job.board.kernel_data_wr_id == set( [        'esr', 'k', 'c' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )
      if ( not ( self.job.board.kernel_data_rd_id == set( [ 'fec', 'fcc',      'm' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )

    if ( ( self.policy_id == 'user' ) and not self._supports_policy_user( self.policy_spec ) ) :
      raise Exception( 'unsupported kernel policy' )
    if ( ( self.policy_id == 'tvla' ) and not self._supports_policy_tvla( self.policy_spec ) ) :
      raise Exception( 'unsupported kernel policy' )
