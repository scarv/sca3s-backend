# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which
# can be found at https://opensource.org/licenses/MIT (or should be included
# as LICENSE.txt within the associated archive or repository).

import tempfile, zipfile
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

    self.verify        = bool( self.depo_spec.get( 'verify'      ) )

  def transfer( self ) :
    session  = boto3.Session( aws_access_key_id = self.access_key_id, aws_secret_access_key = self.access_key, region_name = self.region_id )
    resource = session.resource( 's3' )
    bucket   = resource.Bucket( self.bucket_id )

    def zip_directory(path, zipf):
      for root, dirs, files in os.walk(path):
        for file in files:
          zipf.write(os.path.join(root, file))

    with tempfile.TemporaryFile() as tmp:
      with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as archive:
        zip_directory(self.job.path, archive)
      # Reset file pointer and return zip data (don't think this is required, but left for raw read if needed...)
      # tmp.seek(0)
      # I'll let you deal with the log messages...
      # self.job.log.debug('[src=%s] --> [dst=%s]' % (os.path.relpath(tmp.name, start=self.job.path), dst))
      bucket.upload_file(tmp, self.job.conf['id'][:10] + '.zip')

    self.job.log.shutdown()
