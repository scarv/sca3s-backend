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

    if   ( self.modeof == 'enc' ) :
      self.sizeof_k = self.data_wr_size[ 'k' ]
      self.sizeof_a = self.data_wr_size[ 'a' ]
      self.sizeof_c = self.data_wr_size[ 'm' ]
      self.sizeof_m = self.data_rd_size[ 'c' ]
    elif ( self.modeof == 'dec' ) :
      self.sizeof_k = self.data_wr_size[ 'k' ]
      self.sizeof_a = self.data_wr_size[ 'a' ]
      self.sizeof_c = self.data_wr_size[ 'c' ]
      self.sizeof_m = self.data_rd_size[ 'm' ]

  @abc.abstractmethod
  def kernel_enc( self, k, a, m ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def kernel_dec( self, k, a, c ) :
    raise NotImplementedError()

  def policy_user_init( self, spec             ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    if   ( self.modeof == 'enc' ) :
      k = self.expand( user_value.get( 'k' ) )
      a = self.expand( user_value.get( 'a' ) )
      x = self.expand( user_value.get( 'm' ) )
    elif ( self.modeof == 'dec' ) :
      k = self.expand( user_value.get( 'k' ) )
      a = self.expand( user_value.get( 'a' ) )
      c = self.expand( user_value.get( 'c' ) )

    return { 'k' : k, 'a' : a, 'x' : x }

  def policy_user_step( self, spec, n, i, data ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    k = data[ 'k' ]
    a = data[ 'a' ]
    x = data[ 'x' ]

    if   ( self.modeof == 'enc' ) :
      k = self.expand( user_value.get( 'k' ) ) if ( user_select.get( 'k' ) == 'each' ) else ( k )
      a = self.expand( user_value.get( 'a' ) ) if ( user_select.get( 'a' ) == 'each' ) else ( a )
      x = self.expand( user_value.get( 'm' ) ) if ( user_select.get( 'm' ) == 'each' ) else ( x )
    elif ( self.modeof == 'dec' ) :
      k = self.expand( user_value.get( 'k' ) ) if ( user_select.get( 'k' ) == 'each' ) else ( k )
      a = self.expand( user_value.get( 'a' ) ) if ( user_select.get( 'a' ) == 'each' ) else ( a )
      x = self.expand( user_value.get( 'c' ) ) if ( user_select.get( 'c' ) == 'each' ) else ( x )

    return { 'k' : k, 'a' : a, 'x' : x }
