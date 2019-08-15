# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share  as share

from acquire import board  as board
from acquire import scope  as scope
from acquire import driver as driver

from acquire import repo   as repo
from acquire import depo   as depo

import boto3, os

class DepoImp( depo.DepoAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.access_key_id = share.sys.conf.get( 'creds', section = 'security' ).get( 'access-key-id', section = 'aws' )
    self.access_key    = share.sys.conf.get( 'creds', section = 'security' ).get( 'access-key',    section = 'aws' )

    self.region_id     =       self.depo_spec.get( 'region-id'   )
    self.bucket_id     =       self.depo_spec.get( 'bucket-id'   )

    self.verify        = bool( self.depo_spec.get( 'verify'      ) )

  def transfer( self ) :
    session  = boto3.Session( aws_access_key_id = self.access_key_id, aws_secret_access_key = self.access_key, region_name = self.region_id )
    resource = session.resource( 's3' )
    bucket   = resource.Bucket( self.bucket_id )

    def copy( src, quiet = False ) :
      dst = os.path.join( self.job.user_id, self.job.id, os.path.relpath( src, start = self.job.path ) )

      if ( not quiet ) :
        self.job.log.debug( '[src=%s] --> [dst=%s]' % ( os.path.relpath( src, start = self.job.path ), dst ) )

      with open( src, 'rb' ) as data :
        r = bucket.put_object( Key = dst, Body = data )

        if ( ( self.verify ) and ( r.e_tag.strip( '"' ) != share.util.MD5( src ) ) ) :
          raise Exception()

    log = os.path.join( self.job.path, 'job.log' )
  
    for ( dir, dirs, files ) in os.walk( self.job.path ) :
      for src in [ os.path.join( dir, file ) for file in files ] :
        if ( src != log ) :  
          copy( src, quiet = False )

    self.job.log.shutdown() ; copy( log, quiet = True )
