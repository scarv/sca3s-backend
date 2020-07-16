# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import abc

class DepoAbs( abc.ABC ) :
  def __init__( self, job ) :
    self.job       = job

    self.depo_id   = self.job.conf.get( 'depo_id'   )
    self.depo_spec = self.job.conf.get( 'depo_spec' )

  @abc.abstractmethod
  def transfer( self ) :
    raise NotImplementedError()    
