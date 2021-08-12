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
  def __init__( self, nameof, typeof, data_wr_id, data_wr_size, data_rd_id, data_rd_size ) :
    super().__init__( nameof, typeof, data_wr_id, data_wr_size, data_rd_id, data_rd_size )

    if   ( self.typeof == 'enc' ) :
      self.sizeof_k = self.data_wr_size[ 'k' ]
      self.sizeof_c = self.data_wr_size[ 'm' ]
      self.sizeof_m = self.data_rd_size[ 'c' ]
    elif ( self.typeof == 'dec' ) :
      self.sizeof_k = self.data_wr_size[ 'k' ]
      self.sizeof_c = self.data_wr_size[ 'c' ]
      self.sizeof_m = self.data_rd_size[ 'm' ]

  @abc.abstractmethod
  def kernel_enc( self, k, m ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def kernel_dec( self, k, c ) :
    raise NotImplementedError()

  def policy_user_init( self, spec             ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    if   ( self.typeof == 'enc' ) :
      k = user_value.get( 'k' )
      x = user_value.get( 'm' )
    elif ( self.typeof == 'dec' ) :
      k = user_value.get( 'k' )
      c = user_value.get( 'c' )

    return ( k, x )

  def policy_user_iter( self, spec, n, i, k, x ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    if   ( self.typeof == 'enc' ) :
      k = user_value.get( 'k' ) if ( user_select.get( 'k' ) == 'each' ) else ( k )
      x = user_value.get( 'm' ) if ( user_select.get( 'm' ) == 'each' ) else ( x )
    elif ( self.typeof == 'dec' ) :
      k = user_value.get( 'k' ) if ( user_select.get( 'k' ) == 'each' ) else ( k )
      x = user_value.get( 'c' ) if ( user_select.get( 'c' ) == 'each' ) else ( x )

    return ( k, x )

  @abc.abstractmethod
  def policy_tvla_init_lhs( self, spec             ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def policy_tvla_iter_lhs( self, spec, n, i, k, x ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def policy_tvla_init_rhs( self, spec             ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def policy_tvla_iter_rhs( self, spec, n, i, k, x ) :
    raise NotImplementedError()
