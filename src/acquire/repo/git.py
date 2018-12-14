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

    schema = {
      'type' : 'object', 'default' : {}, 'properties' : {  
        'url' : { 'type' : 'string'                       },
        'tag' : { 'type' : 'string', 'default' : 'master' }
      }
    }  

    share.conf.validate( self.repo_spec, schema )

    self.url = self.repo_spec.get( 'url' )
    self.tag = self.repo_spec.get( 'tag' )

  def _validate_repo_spec( self ) :
    t = { 'url' : { 'default' :     None, 'option' : None, 'type' : str },
          'tag' : { 'default' : 'master', 'option' : None, 'type' : str } }

    self.repo_spec.validate( t )

  def transfer( self ) :
    env = { 'CACHE' : share.sys.conf.get( 'git', section = 'path' ) }

    self.job.extern( [ 'git', 'clone', '--verbose', '--depth', '1', '--branch', self.tag, self.url, 'target' ], env = env )
