# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend as be
from sca3s import spec    as spec

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import abc

class Block( kernel.KernelAbs ) :
  def __init__( self, sizeof_k, sizeof_r, sizeof_m, sizeof_c ) :
    super().__init__()

    self.sizeof_k = sizeof_k
    self.sizeof_r = sizeof_r
    self.sizeof_m = sizeof_m
    self.sizeof_c = sizeof_c

  @abc.abstractmethod
  def enc( self, k, m ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def dec( self, k, c ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def tvla_lhs_init( self, mode ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def tvla_rhs_init( self, mode ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def tvla_lhs_step( self, mode, k, x ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def tvla_rhs_step( self, mode, k, x ) :
    raise NotImplementedError()
