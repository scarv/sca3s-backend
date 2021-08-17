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
  def __init__( self, nameof, modeof, data_wr_id, data_wr_size, data_rd_id, data_rd_size ) :
    super().__init__( nameof, modeof, data_wr_id, data_wr_size, data_rd_id, data_rd_size )

    self.sizeof_x = self.data_wr_size[ 'x' ]
    self.sizeof_r = self.data_wr_size[ 'r' ]

  @abc.abstractmethod
  def model( self, x ) :
    raise NotImplementedError()

  def policy_user_init( self, spec             ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    x = self.expand( user_value.get( 'x' ) )

    return { 'x' : x }

  def policy_user_step( self, spec, n, i, data ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    x = self.expand( user_value.get( 'x' ) ) if ( user_select.get( 'x' ) == 'each' ) else ( data[ 'x' ] )

    return { 'x' : x }
