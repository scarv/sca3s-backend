# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import abc, enum, os, requests, time, urllib.parse

class JSONStatus( enum.IntEnum ):
    """
    Class to define status codes for use with the OKException class.
    By default `status : 0` should be included with all API requests.
    """
    # Global Success Code
    SUCCESS = 0
    # Job error codes
    NO_ITEMS_ON_QUEUE = 1000
    INVALID_JOB_SYNTAX = 1001
    TOO_MANY_QUEUED_JOBS = 1002
    JOB_DOES_NOT_EXIST = 1003
    # User error codes
    NOT_LOGGED_IN = 2000
    # AWS Error Codes
    AWS_AUTHENTICATION_FAILED = 3000
    S3_URL_GENERATION_FAILED = 3001
    # Acquisition Error Codes
    FAILURE_VALIDATING_JOB = 4000
    FAILURE_ALLOCATING_JOB = 4001
    FAILURE_PROCESSING_JOB = 4002
    # Analysis Error Codes
    TVLA_FAILURE = 4003

class APIAbs( abc.ABC ) :
  def __init__( self ) :
    super().__init__()  

    self.url         =      sca3s_be.share.sys.conf.get( 'url',         section = 'api' )

    self.instance    =      sca3s_be.share.sys.conf.get( 'instance',    section = 'api' )

    self.retry_wait  = int( sca3s_be.share.sys.conf.get( 'retry_wait',  section = 'api' ) )
    self.retry_count = int( sca3s_be.share.sys.conf.get( 'retry_count', section = 'api' ) )

  def _request( self, request, url, params = dict(), headers = dict(), json = dict() ) :
    url = urllib.parse.urljoin( self.url, url )
       
    headers = { **headers, "Authorization" : "infrastructure " + os.environ[ 'INFRASTRUCTURE_TOKEN' ] }

    for i in range( self.retry_count ) :
      response = request( url, params = params, headers = headers, json = json )

      if ( response.status_code == 200 ):
        response = response.json()

        if ( response[ "status" ] == JSONStatus.SUCCESS ):
          return response
        else :
          return None

      else :
        sca3s_be.share.sys.log.indent_inc( message = 'API request failed (%d of %d)' % ( i + 1, self.retry_count ) )

        sca3s_be.share.sys.log.info( 'config: url      = ' + str( url      ) )
        sca3s_be.share.sys.log.info( 'config: params   = ' + str( params   ) )
        sca3s_be.share.sys.log.info( 'config: headers  = ' + str( headers  ) )
        sca3s_be.share.sys.log.info( 'config: json     = ' + str( json     ) )

        sca3s_be.share.sys.log.info( '> request        = ' + str( request  ) )
        sca3s_be.share.sys.log.info( '< response       = ' + str( response ) )

        sca3s_be.share.sys.log.indent_dec()

        time.sleep( self.retry_wait )

    raise Exception()

  @abc.abstractmethod
  def retrieve( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def complete( self, job_id, error_code = None ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def announce( self ) :
    raise NotImplementedError()
