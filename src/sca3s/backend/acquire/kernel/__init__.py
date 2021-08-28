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

class KernelAbs( abc.ABC ) :
  def __init__( self, nameof, modeof, data_wr, data_rd ) :
    self.nameof = nameof
    self.modeof = modeof

    ( self.data_wr_id, self.data_wr_size, self.data_wr_type ) = data_wr
    ( self.data_rd_id, self.data_rd_size, self.data_rd_type ) = data_rd

  # Expand an (abstract, symbolic) value description into a (concrete) sequence of bytes.

  def expand( self, x ) :
    if   ( type( x ) == tuple ) :
      return tuple( [     self._expand( v )   for      v   in x         ] )
    elif ( type( x ) == dict  ) :
      return dict( [ ( k, self._expand( v ) ) for ( k, v ) in x.items() ] )
    elif ( type( x ) == str   ) :
      return sca3s_be.share.util.value( x, ids = { **self.data_wr_size, **self.data_rd_size } )

    return x

  def _policy_tvla_init_lhs( self, spec,            ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    data        = dict()

    for id in self.data_wr_id :
      if ( id == 'esr' ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ] )
      else :
        if  ( tvla_mode == 'fvr_k' ) : #  fixed key,      random data (vs.  random key, random data)
          if ( '$' in self.data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ], seed = 0x00 )
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ], seed = 0x01 )
        elif( tvla_mode == 'fvr_d' ) : #  fixed key,      fixed  data (vs.  fixed  key, random data)
          if ( '$' in self.data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ], seed = 0x02 ) # LHS = RHS
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ], seed = 0x03 )
        elif( tvla_mode == 'rvr_d' ) : #  fixed key,      random data (vs.  fixed  key, random data)
          if ( '$' in self.data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ], seed = 0x04 ) # LHS = RHS
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ], seed = 0x05 )

    return data
    
  def _policy_tvla_init_rhs( self, spec,            ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    data        = dict()

    for id in self.data_wr_id :
      if ( id == 'esr' ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ] )
      else :
        if  ( tvla_mode == 'fvr_k' ) : # (fixed key,      random data  vs.) random key, random data
          if ( '$' in self.data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ], seed = 0x10 )
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ], seed = 0x11 )
        elif( tvla_mode == 'fvr_d' ) : # (fixed key,      fixed  data  vs.) fixed  key, random data
          if ( '$' in self.data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ], seed = 0x02 ) # LHS = RHS
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ], seed = 0x13 )
        elif( tvla_mode == 'rvr_d' ) : # (fixed key,      random data  vs.) fixed  key, random data
          if ( '$' in self.data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ], seed = 0x04 ) # LHS = RHS
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ], seed = 0x15 )

    return data

  def _policy_tvla_step_lhs( self, spec, n, i, data ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    for id in self.data_wr_id :
      if ( id == 'esr' ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ] )
      else :
        if  ( tvla_mode == 'fvr_k' ) : #  fixed key,      random data (vs.  random key, random data)
          if ( '$' in self.data_wr_type[ id ] ) :
            pass
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ] )
        elif( tvla_mode == 'fvr_d' ) : #  fixed key,      fixed  data (vs.  fixed  key, random data)
          if ( '$' in self.data_wr_type[ id ] ) :
            pass
          else :
            pass
        elif( tvla_mode == 'rvr_d' ) : #  fixed key,      random data (vs.  fixed  key, random data)
          if ( '$' in self.data_wr_type[ id ] ) :
            pass
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ] )

    return data

  def _policy_tvla_step_rhs( self, spec, n, i, data ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    for id in self.data_wr_id :
      if ( id == 'esr' ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ] )
      else :
        if  ( tvla_mode == 'fvr_k' ) : # (fixed key,      random data  vs.) random key, random data
          if ( '$' in self.data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ] )
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ] )
        elif( tvla_mode == 'fvr_d' ) : # (fixed key,      fixed  data  vs.) fixed  key, random data
          if ( '$' in self.data_wr_type[ id ] ) :
            pass
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ] )
        elif( tvla_mode == 'rvr_d' ) : # (fixed key,      random data  vs.) fixed  key, random data
          if ( '$' in self.data_wr_type[ id ] ) :
            pass
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ] )

    return data

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

  def policy_user_init( self, spec             ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    data        = dict()

    for id in self.data_wr_id :
      if ( id == 'esr' ) :
        data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ] )
      else :
        data[ id ] = self.expand( user_value.get( id ) )

    return data

  def policy_user_step( self, spec, n, i, data ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    for id in self.data_wr_id :
      if ( id == 'esr' ) :
        data[ id ] = sca3s_be.share.util.randbytes( self.data_wr_size[ id ] )
      else :
        data[ id ] = self.expand( user_value.get( id ) ) if ( user_select.get( id ) == 'each' ) else ( data[ id ] )

    return data

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
