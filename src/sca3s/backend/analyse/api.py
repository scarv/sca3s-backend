# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which
# can be found at https://opensource.org/licenses/MIT (or should be included
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import requests, urllib.parse

class APIImp( sca3s_be.share.api.APIAbs ):
  def __init__( self ) :
    super().__init__()  

  def retrieve( self ):
    url  =                       'api/acquire/job'
    json = {}

    return self._request( requests.get,   url, json = json )

  def complete( self, job_id, job_status, job_response ):
    if ( job_id == None ) :
      return

    url  = urllib.parse.urljoin( 'api/acquire/job/', job_id )
    json = { 'status' : job_status.hex(), 'response' : job_response }

    return self._request( requests.patch, url, json = json )

  def announce( self ):
    url  =                       'api/acquire/advertise'
    json = {}

    if ( self.instance != '*' ) :
      json[ 'queue' ] = self.instance

    return self._request( requests.post,  url, json = json )
