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

import boto3, os

class DepoImp( depo.DepoAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.access_key_id = sca3s_be.share.sys.conf.get( 'creds', section = 'security' ).get( 'access_key_id', section = 's3' )
    self.access_key    = sca3s_be.share.sys.conf.get( 'creds', section = 'security' ).get( 'access_key',    section = 's3' ) 

    self.region_id     = self.depo_spec.get( 'region_id' )
    self.bucket_id     = self.depo_spec.get( 'bucket_id' )

  def transfer( self ) :
    session  = boto3.Session( aws_access_key_id = self.access_key_id, aws_secret_access_key = self.access_key, region_name = self.region_id )
    bucket   = session.resource( 's3' ).Bucket( self.bucket_id )
    
    self.job.log.shutdown()

    def upload( name, ext ) :
      bucket.upload_file( os.path.join( self.job.path, name ), os.path.join( str( self.job.user_id ), self.job.job_id[ : 10 ] + ext ) )

    upload( 'acquire.log',     '.log'     )
    upload( 'acquire.hdf5.gz', '.hdf5.gz' )
