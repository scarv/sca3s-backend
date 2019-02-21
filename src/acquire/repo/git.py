# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire        import share  as share

from acquire.device import board  as board
from acquire.device import scope  as scope
from acquire        import driver as driver

from acquire        import repo   as repo
from acquire        import depo   as depo

class RepoImp( repo.RepoAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.url = self.repo_spec.get( 'url' )
    self.tag = self.repo_spec.get( 'tag' )

  def transfer( self ) :
    env = { 'CACHE' : share.sys.conf.get( 'git', section = 'path' ) }

    print( self.url )
    print( self.tag )

    self.job.extern( [ 'git', 'clone', '--verbose', '--depth', '1', '--branch', self.tag, self.url, 'target' ], env = env )
