# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

import sca3s_backend as be
import sca3s_spec    as spec

from sca3s_backend.acquire import board  as board
from sca3s_backend.acquire import scope  as scope
from sca3s_backend.acquire import driver as driver

from sca3s_backend.acquire import repo   as repo
from sca3s_backend.acquire import depo   as depo

import git, os

class RepoImp( repo.RepoAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.url  = self.repo_spec.get( 'url'  )
    self.tag  = self.repo_spec.get( 'tag'  )
    self.conf = self.repo_spec.get( 'conf' )

  def transfer( self ) :
    git.Repo.clone_from( self.url, os.path.join( self.job.path, 'target' ), branch = self.tag, depth = 1 )
