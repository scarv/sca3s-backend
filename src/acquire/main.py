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

from acquire        import server as server

import flask, os, queue, shutil, tempfile, threading, time

#app = flask.Flask( __name__ ) ; jobs = queue.Queue( 1 )

def process( manifest ) :
    share.sys.log.info( '|>>> validating job' )

    db = share.sys.conf.get( 'device-db', section = 'job' )

    if ( manifest.has( 'device-id' ) ) :
      t =  manifest.get( 'device-id' )

      if ( db.has( t ) ) :
        for ( key, value ) in db.get( t ).items() :
          manifest.put( key, value )
      else :
        raise share.exception.ConfigurationException()

    share.schema.validate( manifest, share.schema.SCHEMA_JOB ) ; id = manifest.get( 'id' )

    share.sys.log.info( '|>>> processing job id = %s' % ( id ) )

    path = tempfile.mkdtemp( prefix = id + '.', dir = share.sys.conf.get( 'job', section = 'path' ) ) ; os.chdir( path ) ; log = share.log.build_log_job( name = id )

    job = share.job.Job( manifest, path, log )

    job.process_prologue()
    job.process()
    job.process_epilogue()

    if ( share.sys.conf.get( 'clean', section = 'job' ) ) :
      shutil.rmtree( path )

    share.sys.log.info( '|<<< processing job id = %s' % ( id ) )

#def server_worker() :
#  while( True ) :
#    process( share.conf.Conf( conf = jobs.get() ) )
#
#@app.route( '/api/device', methods = [ 'GET', 'POST' ] )
#def server_api_device() :
#  t = dict()
#
#  for ( key, value ) in share.sys.conf.get( 'device-db', section = 'job' ).items() :
#    t[ key ] = { 'board-desc' : value[ 'board-desc' ],
#                 'scope-desc' : value[ 'scope-desc' ] }
#
#  return flask.jsonify( t )
#
#@app.route( '/api/submit', methods = [ 'GET', 'POST' ] )
#def server_api_submit() :
#  try :
#    share.sys.log.info( '!>>> queueing job' )
#
#    jobs.put( flask.request.get_json() )
#
#    share.sys.log.info( '!<<< queueing job' )
#  except Exception as e :
#    raise e
#
#  return ""

if ( __name__ == '__main__' ) :
  try :
    share.sys.init()
  except Exception as e :
    raise e

  try :
#    if   ( share.sys.conf.get( 'mode', section = 'sys' ) == 'server' ) :
#      threading.Thread( target = server_worker ).start() ; app.run()
#
#    elif ( share.sys.conf.get( 'mode', section = 'sys' ) == 'cli'    ) :
#      if   ( share.sys.conf.has( 'manifest-file', section = 'job' ) ) :
#        manifest = share.conf.Conf( conf = share.sys.conf.get( 'manifest-file', section = 'job' ) )
#      elif ( share.sys.conf.has( 'manifest-data', section = 'job' ) ) :
#        manifest = share.conf.Conf( conf = share.sys.conf.get( 'manifest-data', section = 'job' ) )
#      else :
#        raise Exception()
#  
#      process( manifest )

    remote = server.remote.Remote()
    
    while( True ) :
      share.sys.log.info( 'start wait' )
      time.sleep( 1 )
      share.sys.log.info( 'end   wait' )

      share.sys.log.info( 'start fetch' )
      manifest = remote.receive_job()
      share.sys.log.info( 'end   fetch' )

      if ( manifest != None ) :
        process( manifest )

  except Exception as e :
    raise e
