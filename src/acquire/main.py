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

  share.schema.validate( manifest, share.schema.SCHEMA_JOB )

  share.sys.log.info( '|<<< validating job' )

  id = manifest.get( 'id' )

  share.sys.log.info( '|>>> processing job id = %s' % ( id ) )

  path = tempfile.mkdtemp( prefix = id + '.', dir = share.sys.conf.get( 'job', section = 'path' ) ) ; os.chdir( path ) ; log = share.log.build_log_job( name = id )

  job = share.job.Job( manifest, path, log )

  job.process_prologue()
  job.process()
  job.process_epilogue()

  if ( share.sys.conf.get( 'clean', section = 'job' ) ) :
    shutil.rmtree( path )

  share.sys.log.info( '|<<< processing job id = %s' % ( id ) )

  return id

def mode_cli() :
  if   ( share.sys.conf.has( 'manifest-file', section = 'job' ) ) :
    manifest = share.conf.Conf( conf = share.sys.conf.get( 'manifest-file', section = 'job' ) )
  elif ( share.sys.conf.has( 'manifest-data', section = 'job' ) ) :
    manifest = share.conf.Conf( conf = share.sys.conf.get( 'manifest-data', section = 'job' ) )

  process( manifest )

def mode_server_push() :
  server_host  =      sys.conf.get( 'host', section = 'server-push' )
  server_port  = int( sys.conf.get( 'port', section = 'server-push' ) )

  server       = flask.Flask( __name__, host = server_host, port = server_port ) 
      
  @server.route( '/api/device', methods = [ 'GET', 'POST' ] )
  def server_api_device() :
    t = dict()
      
    for ( key, value ) in share.sys.conf.get( 'device-db', section = 'job' ).items() :
      t[ key ] = { 'board-desc' : value[ 'board-desc' ],
                   'scope-desc' : value[ 'scope-desc' ] }
      
    return flask.jsonify( t )
      
  @server.route( '/api/submit', methods = [ 'GET', 'POST' ] )
  def server_api_submit() :
    share.sys.log.info( '|<<< pushing job' )
    manifest = flask.request.get_json()
    share.sys.log.info( '|>>> pushing job' )

    process( share.conf.Conf( conf = manifest ) )

    return ""
      
  server.run()

def mode_server_pull() :
  server = server.remote.Remote() ; db = list( share.sys.conf.get( 'device-db', section = 'job' ).keys() )
      
  while( True ) :
    share.sys.log.info( '|<<< pulling job' )
    manifest = remote.receive_job( db )
    share.sys.log.info( '|>>> pulling job' )
  
    if ( manifest != None ) :
      remote.complete_job( process( share.conf.Conf( conf = manifest ) ) )

    time.sleep( sys.conf.get( 'poll', section = 'server-pull' ) )

if ( __name__ == '__main__' ) :
  try :
    share.sys.init()

    if   ( share.sys.conf.get( 'mode', section = 'sys' ) == 'cli'         ) :
      mode_cli()
    elif ( share.sys.conf.get( 'mode', section = 'sys' ) == 'server-push' ) :
      mode_server_push()
    elif ( share.sys.conf.get( 'mode', section = 'sys' ) == 'server-pull' ) :
      mode_server_pull()

  except Exception as e :
    raise e
