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

  def _policy_tvla_init_lhs( self, spec,            ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if   ( self.modeof == 'enc' ) :
      sizeof_k = self.sizeof_k ; sizeof_x = self.sizeof_m
    elif ( self.modeof == 'dec' ) :
      sizeof_k = self.sizeof_k ; sizeof_x = self.sizeof_c

    if  ( tvla_mode == 'fvr_k' ) : #  fixed key,      random data (vs.  random key, random data)
      k = sca3s_be.share.util.randbytes( sizeof_k )
      x = sca3s_be.share.util.randbytes( sizeof_x )
    elif( tvla_mode == 'fvr_d' ) : #  fixed key,      fixed  data (vs.  fixed  key, random data)
      k = sca3s_be.share.util.randbytes( sizeof_k )
      x = sca3s_be.share.util.randbytes( sizeof_x )
    elif( tvla_mode == 'rvr_d' ) : #  fixed key,      random data (vs.  fixed  key, random data)
      k = sca3s_be.share.util.randbytes( sizeof_k )
      x = sca3s_be.share.util.randbytes( sizeof_x )

    if   ( self.modeof == 'enc' ) :
      return { 'k' : k, 'm' : x }  
    elif ( self.modeof == 'dec' ) :
      return { 'k' : k, 'c' : x }  
    
  def _policy_tvla_init_rhs( self, spec,            ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if   ( self.modeof == 'enc' ) :
      sizeof_k = self.sizeof_k ; sizeof_x = self.sizeof_m
    elif ( self.modeof == 'dec' ) :
      sizeof_k = self.sizeof_k ; sizeof_x = self.sizeof_c

    if  ( tvla_mode == 'fvr_k' ) : #  fixed key,      random data (vs.  random key, random data)
      k = sca3s_be.share.util.randbytes( sizeof_k )
      x = sca3s_be.share.util.randbytes( sizeof_x )
    elif( tvla_mode == 'fvr_d' ) : #  fixed key,      fixed  data (vs.  fixed  key, random data)
      k = sca3s_be.share.util.randbytes( sizeof_k )
      x = sca3s_be.share.util.randbytes( sizeof_x )
    elif( tvla_mode == 'rvr_d' ) : #  fixed key,      random data (vs.  fixed  key, random data)
      k = sca3s_be.share.util.randbytes( sizeof_k )
      x = sca3s_be.share.util.randbytes( sizeof_x )

    if   ( self.modeof == 'enc' ) :
      return { 'k' : k, 'm' : x }  
    elif ( self.modeof == 'dec' ) :
      return { 'k' : k, 'c' : x }  

  def _policy_tvla_step_lhs( self, spec, n, i, data ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if   ( self.modeof == 'enc' ) :
      sizeof_k = self.sizeof_k ; sizeof_x = self.sizeof_m ; k = data[ 'k' ] ; x = data[ 'm' ]
    elif ( self.modeof == 'dec' ) :
      sizeof_k = self.sizeof_k ; sizeof_x = self.sizeof_c ; k = data[ 'k' ] ; x = data[ 'c' ]

    if  ( tvla_mode == 'fvr_k' ) : #  fixed key,      random data (vs.  random key, random data)
      k = k
      x = sca3s_be.share.util.randbytes( sizeof_x )
    elif( tvla_mode == 'fvr_d' ) : #  fixed key,      fixed  data (vs.  fixed  key, random data)
      k = k
      x = x
    elif( tvla_mode == 'rvr_d' ) : #  fixed key,      random data (vs.  fixed  key, random data)
      k = k
      x = sca3s_be.share.util.randbytes( sizeof_x )

    if   ( self.modeof == 'enc' ) :
      return { 'k' : k, 'm' : x }  
    elif ( self.modeof == 'dec' ) :
      return { 'k' : k, 'c' : x }  

  def _policy_tvla_step_rhs( self, spec, n, i, data ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if   ( self.modeof == 'enc' ) :
      sizeof_k = self.sizeof_k ; sizeof_x = self.sizeof_m ; k = data[ 'k' ] ; x = data[ 'm' ]
    elif ( self.modeof == 'dec' ) :
      sizeof_k = self.sizeof_k ; sizeof_x = self.sizeof_c ; k = data[ 'k' ] ; x = data[ 'c' ]

    if  ( tvla_mode == 'fvr_k' ) : # (fixed key,      random data  vs.) random key, random data
      k = sca3s_be.share.util.randbytes( sizeof_k )
      x = sca3s_be.share.util.randbytes( sizeof_x )
    elif( tvla_mode == 'fvr_d' ) : # (fixed key,      fixed  data  vs.) fixed  key, random data
      k = k
      x = sca3s_be.share.util.randbytes( sizeof_x )
    elif( tvla_mode == 'rvr_d' ) : # (fixed key,      random data  vs.) fixed  key, random data
      k = k
      x = sca3s_be.share.util.randbytes( sizeof_x )

    if   ( self.modeof == 'enc' ) :
      return { 'k' : k, 'm' : x }  
    elif ( self.modeof == 'dec' ) :
      return { 'k' : k, 'c' : x }  

  def supports_verify( self ) :
    return False

  def supports_policy_user( self, spec ) :
    return True

  def supports_policy_tvla( self, spec ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if  ( tvla_mode == 'fvr_k' ) : #  fixed key,      random data  vs.  random key, random data
      return True
    elif( tvla_mode == 'fvr_d' ) : #  fixed key,      fixed  data  vs.  fixed  key, random data
      return True
    elif( tvla_mode == 'svr_d' ) :#   fixed key, semi-fixed  data  vs.  fixed  key, random data
      return False
    elif( tvla_mode == 'rvr_d' ) : #  fixed key,      random data  vs.  fixed  key, random data
      return True

    return False

  def verify( self, data_wr, data_rd ) :
    if   ( self.modeof == 'enc' ) :
      return False
    elif ( self.modeof == 'dec' ) :
      return False

    return False

  def policy_user_init( self, spec             ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    if   ( self.modeof == 'enc' ) :
      k = self.expand( user_value.get( 'k' ) )
      m = self.expand( user_value.get( 'm' ) )

      return { 'k' : k, 'm' : m }

    elif ( self.modeof == 'dec' ) :
      k = self.expand( user_value.get( 'k' ) )
      c = self.expand( user_value.get( 'c' ) )

      return { 'k' : k, 'c' : c }

  def policy_user_step( self, spec, n, i, data ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    if   ( self.modeof == 'enc' ) :
      k = self.expand( user_value.get( 'k' ) ) if ( user_select.get( 'k' ) == 'each' ) else ( data[ 'k' ] )
      m = self.expand( user_value.get( 'm' ) ) if ( user_select.get( 'm' ) == 'each' ) else ( data[ 'm' ] )

      return { 'k' : k, 'm' : m }

    elif ( self.modeof == 'dec' ) :
      k = self.expand( user_value.get( 'k' ) ) if ( user_select.get( 'k' ) == 'each' ) else ( data[ 'k' ] )
      c = self.expand( user_value.get( 'c' ) ) if ( user_select.get( 'c' ) == 'each' ) else ( data[ 'c' ] )

      return { 'k' : k, 'c' : c }

    return None

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
