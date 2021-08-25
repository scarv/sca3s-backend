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

  @abc.abstractmethod
  def supports_model( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def supports_policy_user( self, spec ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def supports_policy_tvla( self, spec ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def policy_user_init( self, spec                           ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def policy_user_step( self, spec, n, i, data               ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def policy_tvla_init( self, spec,             mode = 'lhs' ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def policy_tvla_step( self, spec, n, i, data, mode = 'lhs' ) :
    raise NotImplementedError()
