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

import binascii, struct

class DriverImp( driver.hash.DriverType ) :
  def __init__( self, job ) :
    super().__init__( job )

  def _supports_verify( self ) :
    return True

  def _verify( self, data_wr, data_rd ) :
    return ( sca3s_be.share.crypto.SHA_2_224().digest( data_wr[ 'm' ] ) ) == ( data_rd[ 'd' ] )
