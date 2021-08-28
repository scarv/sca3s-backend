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

import abc

class KernelType( kernel.KernelAbs ) :
  def __init__( self, nameof, modeof, data_wr, data_rd ) :
    super().__init__( nameof, modeof, data_wr, data_rd )

    if   ( self.modeof == 'default' ) :
      self.modeof   = 'enc'

    if   ( self.modeof == 'enc'     ) :
      self.sizeof_k = self.data_wr_size[ 'k' ]
      self.typeof_k = self.data_wr_type[ 'k' ]
      self.sizeof_m = self.data_wr_size[ 'm' ]
      self.typeof_m = self.data_wr_type[ 'm' ]
      self.sizeof_c = self.data_rd_size[ 'c' ]
      self.typeof_c = self.data_rd_type[ 'c' ]

    elif ( self.modeof == 'dec'     ) :
      self.sizeof_k = self.data_wr_size[ 'k' ]
      self.typeof_k = self.data_wr_type[ 'k' ]
      self.sizeof_m = self.data_rd_size[ 'm' ]
      self.typeof_m = self.data_rd_type[ 'm' ]
      self.sizeof_c = self.data_wr_size[ 'c' ]
      self.typeof_c = self.data_wr_type[ 'c' ]
