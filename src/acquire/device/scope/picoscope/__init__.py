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

class PicoScope( scope.ScopeAbs ) :
  def __init__( self, job, api ) :
    super().__init__( job )

    self.api = api

  def  open( self ) :
    self.device = self.api( serialNumber = self.connect_id.encode(), connect = True )

    if ( self.device == None ) :
      raise Exception()

    for t in self.device.getAllUnitInfo().split( '\n' ) :
      self.job.log.info( t )

  def close( self ) :
    self.device.close()
