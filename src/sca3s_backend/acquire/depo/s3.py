# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

import sca3s_backend as be
import sca3s_spec    as spec

from sca3s_backend.acquire import board  as board
from sca3s_backend.acquire import scope  as scope
from sca3s_backend.acquire import driver as driver

from sca3s_backend.acquire import repo   as repo
from sca3s_backend.acquire import depo   as depo

import boto3, os

class DepoImp( depo.DepoAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.access_key_id = be.share.sys.conf.get( 'creds', section = 'security' ).get( 'access-key-id', section = 's3' )
    self.access_key    = be.share.sys.conf.get( 'creds', section = 'security' ).get( 'access-key',    section = 's3' ) 

    self.region_id     =       self.depo_spec.get( 'region-id'   )
    self.bucket_id     =       self.depo_spec.get( 'bucket-id'   )

  def transfer( self ) :
    session  = boto3.Session( aws_access_key_id = self.access_key_id, aws_secret_access_key = self.access_key, region_name = self.region_id )
    bucket   = session.resource( 's3' ).Bucket( self.bucket_id )
    
    self.job.log.shutdown()

    bucket.upload_file( os.path.join( self.job.path, 'acquire.log'    ), self.job.id[ : 10 ] + '.log'    )
    bucket.upload_file( os.path.join( self.job.path, 'acquire.trs.gz' ), self.job.id[ : 10 ] + '.trs.gz' )
