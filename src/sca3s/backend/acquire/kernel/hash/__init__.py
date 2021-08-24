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

    self.sizeof_m = self.data_wr_size[ 'm' ]
    self.sizeof_d = self.data_rd_size[ 'd' ]

  def _policy_tvla_init_lhs( self, spec,            ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    return None
    
  def _policy_tvla_init_rhs( self, spec,            ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    return None

  def _policy_tvla_step_lhs( self, spec, n, i, data ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    return None

  def _policy_tvla_step_rhs( self, spec, n, i, data ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    return None

  def supports_model( self ) :
    return False

  def supports_policy_user( self, spec ) :
    return True

  def supports_policy_tvla( self, spec ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if  ( tvla_mode == 'fvr_k' ) : #  fixed key,      random data  vs.  random key, random data
      return False
    elif( tvla_mode == 'fvr_d' ) : #  fixed key,      fixed  data  vs.  fixed  key, random data
      return False
    elif( tvla_mode == 'svr_d' ) :#   fixed key, semi-fixed  data  vs.  fixed  key, random data
      return False
    elif( tvla_mode == 'rvr_d' ) : #  fixed key,      random data  vs.  fixed  key, random data
      return False

    return False

  def model( self, m ) :
    return None

  def policy_user_init( self, spec             ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    m = self.expand( user_value.get( 'm' ) )

    return { 'm' : m }

  def policy_user_step( self, spec, n, i, data ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    m = self.expand( user_value.get( 'm' ) ) if ( user_select.get( 'm' ) == 'each' ) else ( data[ 'm' ] )

    return { 'm' : m }

  def policy_tvla_init( self, spec,             mode = 'lhs' ) :
    if   ( mode == 'lhs' ) :
      return self._policy_tvla_init_lhs( spec             )
    elif ( mode == 'rhs' ) :
      return self._policy_tvla_init_rhs( spec             )

    return None

  def policy_tvla_step( self, spec, n, i, data, mode = 'lhs' ) :
    if   ( mode == 'lhs' ) :
      return self._policy_tvla_step_lhs( spec, n, i, data )
    elif ( mode == 'rhs' ) :
      return self._policy_tvla_step_rhs( spec, n, i, data )

    return None
