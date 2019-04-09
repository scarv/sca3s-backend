# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share  as share

from acquire import board  as board
from acquire import scope  as scope
from acquire import driver as driver

from acquire import repo   as repo
from acquire import depo   as depo

import os

class DepoImp( depo.DepoAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.path = self.repo_spec.get( 'path' )

  def transfer( self ) :
    self.job.extern( [ 'cp', '--recursive', self.job.path, self.path ] )
