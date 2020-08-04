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

import binascii

class KernelImp( kernel.block.KernelType ) :
  def __init__( self, func, sizeof_k, sizeof_r, sizeof_m, sizeof_c ) :
    super().__init__( func, sizeof_k, sizeof_r, sizeof_m, sizeof_c )

  def supports( self, policy ) :
    if   ( policy == 'user' ) :
      return True
    elif ( policy == 'tvla' ) :
      return False

    return False

  def enc( self, k, m ) :
    return None

  def dec( self, k, c ) :
    return None

  def tvla_init_lhs( self, mode ) :
    return ( None, None )

  def tvla_iter_lhs( self, mode, k, x ) :
    return ( None, None )

  def tvla_init_rhs( self, mode ) :
    return ( None, None )

  def tvla_iter_rhs( self, mode, k, x ) :
    return ( None, None )
