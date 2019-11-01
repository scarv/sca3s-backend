# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend as be
from sca3s import spec    as spec

import abc

class APIAbs( abc.ABC ) :
  def __init__( self ) :
    super().__init__()  

  @abc.abstractmethod
  def retrieve_job( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def complete_job( self, job_id, error_code = None ) :
    raise NotImplementedError()
