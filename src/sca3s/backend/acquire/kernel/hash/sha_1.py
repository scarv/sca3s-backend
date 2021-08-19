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

import binascii, struct

class KernelImp( kernel.block.KernelType ) :
  def __init__( self, nameof, modeof, data_wr_id, data_wr_size, data_rd_id, data_rd_size ) :
    super().__init__( nameof, modeof, data_wr_id, data_wr_size, data_rd_id, data_rd_size )

  def supports_model( self ) :
    return True

  def model( self, m ) :
    return sca3s_be.share.crypto.SHA_1().digest( m )
