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

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import abc

class RepoAbs( abc.ABC ) :
  def __init__( self, job ) :
    self.job       = job

    self.repo_id   = self.job.conf.get( 'repo_id'   )
    self.repo_spec = self.job.conf.get( 'repo_spec' )

  def __str__( self ) :
    return self.repo_id

  @abc.abstractmethod
  def transfer( self ) :
    raise NotImplementedError()    
