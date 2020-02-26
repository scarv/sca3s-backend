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

import requests, urllib.parse

class APIImp( sca3s_be.share.api.APIAbs ):
  def __init__( self ) :
    super().__init__()  

  def retrieve( self ):
    params = dict()

    if ( self.instance != '*' ) :
      params[ 'queue' ] = instance

    return self._request( requests.get, 'api/analyse/job', params = params )

  def complete( self, job_id, status = None ):
    return self._request( requests.patch, urllib.parse.urljoin( 'api/analyse/job', job_id ), json = { 'status' : status } )

  def announce( self ):
    return self._request( requests.post, 'api/analyse/advertise' )
