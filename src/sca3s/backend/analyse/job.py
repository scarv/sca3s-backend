# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

class JobImp( sca3s_be.share.job.JobAbs ) :
  def __init__( self, conf, path, log ) :
    super().__init__( conf, path, log )  

  def execute_prologue( self ) :
    pass

  def execute( self ) :
    pass

  def execute_epilogue( self ) :
    pass
