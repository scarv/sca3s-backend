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
      self.sizeof_m = self.data_wr_size[ 'm' ]
      self.sizeof_c = self.data_rd_size[ 'c' ]
    elif ( self.modeof == 'dec' ) :
      self.sizeof_k = self.data_wr_size[ 'k' ]
      self.sizeof_a = self.data_wr_size[ 'a' ]
      self.sizeof_c = self.data_wr_size[ 'c' ]
      self.sizeof_m = self.data_rd_size[ 'm' ]

  def _policy_tvla_init_lhs( self, spec,            ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if   ( self.modeof == 'enc' ) :
      sizeof_x = self.sizeof_m
    elif ( self.modeof == 'dec' ) :
      sizeof_x = self.sizeof_c

    return None
    
  def _policy_tvla_init_rhs( self, spec,            ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if   ( self.modeof == 'enc' ) :
      sizeof_x = self.sizeof_m
    elif ( self.modeof == 'dec' ) :
      sizeof_x = self.sizeof_c

    return None

  def _policy_tvla_step_lhs( self, spec, n, i, data ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if   ( self.modeof == 'enc' ) :
      sizeof_x = self.sizeof_m
    elif ( self.modeof == 'dec' ) :
      sizeof_x = self.sizeof_c

    return None

  def _policy_tvla_step_rhs( self, spec, n, i, data ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if   ( self.modeof == 'enc' ) :
      sizeof_x = self.sizeof_m
    elif ( self.modeof == 'dec' ) :
      sizeof_x = self.sizeof_c

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

  def model_enc( self, k, a, m ) :
    return None

  def model_dec( self, k, a, c ) :
    return None

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
      x = self.expand( user_value.get( 'c' ) )

    return { 'k' : k, 'a' : a, 'x' : x }

  def policy_user_step( self, spec, n, i, data ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    if   ( self.modeof == 'enc' ) :
      k = self.expand( user_value.get( 'k' ) ) if ( user_select.get( 'k' ) == 'each' ) else ( data[ 'k' ] )
      a = self.expand( user_value.get( 'a' ) ) if ( user_select.get( 'a' ) == 'each' ) else ( data[ 'a' ] )
      x = self.expand( user_value.get( 'm' ) ) if ( user_select.get( 'm' ) == 'each' ) else ( data[ 'x' ] )

    elif ( self.modeof == 'dec' ) :
      k = self.expand( user_value.get( 'k' ) ) if ( user_select.get( 'k' ) == 'each' ) else ( data[ 'k' ] )
      a = self.expand( user_value.get( 'a' ) ) if ( user_select.get( 'a' ) == 'each' ) else ( data[ 'a' ] )
      x = self.expand( user_value.get( 'c' ) ) if ( user_select.get( 'c' ) == 'each' ) else ( data[ 'x' ] )

    return { 'k' : k, 'a' : a, 'x' : x }

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