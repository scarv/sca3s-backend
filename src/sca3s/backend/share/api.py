# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import abc, enum, os, requests, time, urllib.parse

class APIAbs( abc.ABC ) :
  def __init__( self ) :
    super().__init__()  

    self.url         =      sca3s_be.share.sys.conf.get( 'url',         section = 'api' )

    self.instance    =      sca3s_be.share.sys.conf.get( 'instance',    section = 'api' )

    self.retry_wait  = int( sca3s_be.share.sys.conf.get( 'retry_wait',  section = 'api' ) )
    self.retry_count = int( sca3s_be.share.sys.conf.get( 'retry_count', section = 'api' ) )

  def _request( self, request, url, params = dict(), headers = dict(), json = dict() ) :
    url = urllib.parse.urljoin( self.url, url ) ; headers = { **headers, 'Authorization' : 'infrastructure' + ' ' + os.environ[ 'INFRASTRUCTURE_TOKEN' ] }

    for i in range( self.retry_count ) :
      response = request( url, params = params, headers = headers, json = json )

      if ( response.status_code == 200 ):
        response = response.json() ; status_code = sca3s_mw.share.status.Status.build( response[ 'status' ] )

        sca3s_be.share.sys.log.indent_inc( message = 'API request success (%d of %d)' % ( i + 1, self.retry_count ) )
        sca3s_be.share.sys.log.info( '> request  = %s( %s, params = %s, headers = %s, json = %s' % ( str( request  ), url, params, headers, json ) )
        sca3s_be.share.sys.log.info( '< response = %s'                                           % ( str( response )                             ) )
        sca3s_be.share.sys.log.indent_dec()
     
        if ( status_code == sca3s_mw.share.status.Status.SUCCESS ) :
          return response
        else :
          return None

      else :
        sca3s_be.share.sys.log.indent_inc( message = 'API request failure (%d of %d)' % ( i + 1, self.retry_count ) )
        sca3s_be.share.sys.log.info( '> request  = %s( %s, params = %s, headers = %s, json = %s' % ( str( request  ), url, params, headers, json ) )
        sca3s_be.share.sys.log.info( '< response = %s'                                           % ( str( response )                             ) )
        sca3s_be.share.sys.log.indent_dec()

        time.sleep( self.retry_wait )

    raise Exception( 'failed to complete API request' )

  @abc.abstractmethod
  def retrieve( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def complete( self, job_id, status = None ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def announce( self ) :
    raise NotImplementedError()
