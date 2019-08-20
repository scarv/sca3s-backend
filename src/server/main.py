# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

import spec         as spec
import server.share as share

import server.acquire.board  as board
import server.acquire.scope  as scope
import server.acquire.driver as driver

import server.acquire.repo   as repo
import server.acquire.depo   as depo

import server.acquire.server as server

import flask, os, queue, shutil, signal, tempfile, threading, time

STATUS_SUCCESS                = 0

STATUS_FAILURE_VALIDATING_JOB = 1
STATUS_FAILURE_ALLOCATING_JOB = 2
STATUS_FAILURE_PROCESSING_JOB = 3

def process( manifest ) :
  id = None ; result = STATUS_SUCCESS

  try :
    share.sys.log.info( '|> validating job' )
  
    try :
      db = share.sys.conf.get( 'device-db', section = 'job' )
    
      if ( manifest.has( 'device-id' ) ) :
        t =  manifest.get( 'device-id' )
    
        if ( db.has( t ) ) :
          for ( key, value ) in db.get( t ).items() :
            manifest.put( key, value )
        else :
          raise share.exception.ConfigurationException()
    
      share.schema.validate( manifest, spec.acquire.SCHEMA )
  
    except Exception as e :
      result = STATUS_FAILURE_VALIDATING_JOB ; raise e

    share.sys.log.info( '|< validating job' )

    share.sys.log.info( '|> allocating job' )

    try :
      id = manifest.get( 'id' ) ; 

      path = tempfile.mkdtemp( prefix = id + '.', dir = share.sys.conf.get( 'job', section = 'path' ) )
      os.chdir( path ) 
      log = share.log.build_log_job( name = id, replace = { path : '${JOB}', os.path.basename( path ) : '${JOB}' } )
      job = share.job.Job( manifest, path, log )

    except Exception as e :
      result = STATUS_FAILURE_ALLOCATING_JOB ; raise e

    share.sys.log.info( '|< allocating job' )

    share.sys.log.info( '|> processing job' )

    try :    
      job.process_prologue()
      job.process()
      job.process_epilogue()
  
    except Exception as e :
      result = STATUS_FAILURE_PROCESSING_JOB ; raise e

    if ( share.sys.conf.get( 'clean', section = 'job' ) ) :
      shutil.rmtree( path, ignore_errors = True )

    share.sys.log.info( '|< processing job' )

  except Exception as e :
    share.exception.dump( e, log = share.sys.log )

  return ( id, result )

def run_cli() :
  if   ( share.sys.conf.has( 'manifest-file', section = 'job' ) ) :
    manifest = share.conf.Conf( conf = share.sys.conf.get( 'manifest-file', section = 'job' ) )
  elif ( share.sys.conf.has( 'manifest-data', section = 'job' ) ) :
    manifest = share.conf.Conf( conf = share.sys.conf.get( 'manifest-data', section = 'job' ) )
  else :
    raise share.exception.ConfigurationException()

  process( manifest )

def run_api() :
  server_pull      = server.remote.Remote()
      
  server_pull_wait = int( share.sys.conf.get( 'wait', section = 'server-pull' ) )
  server_pull_ping = int( share.sys.conf.get( 'ping', section = 'server-pull' ) )

  term = False ; ping = 0 ; db = list( share.sys.conf.get( 'device-db', section = 'job' ).keys() )

  def signalHandler( signum, frame ) :
    nonlocal term

    if   ( signum == signal.SIGABRT ) :
      term = True
    elif ( signum == signal.SIGTERM ) :
      term = True

    return

  signal.signal( signal.SIGABRT, signalHandler )
  signal.signal( signal.SIGTERM, signalHandler )

  while( True ) :
    manifest = server_pull.receive_job( db )
  
    if ( manifest != None ) :
      ( id, result ) = process( share.conf.Conf( conf = manifest ) )

      if ( id != None ) :
        if   ( result == STATUS_SUCCESS                ) :
          server_pull.complete_job( id, error_code = server.status.JSONStatus.SUCCESS                )
        elif ( result == STATUS_FAILURE_VALIDATING_JOB ) :
          server_pull.complete_job( id, error_code = server.status.JSONStatus.FAILURE_VALIDATING_JOB )
        elif ( result == STATUS_FAILURE_ALLOCATING_JOB ) :
          server_pull.complete_job( id, error_code = server.status.JSONStatus.FAILURE_ALLOCATING_JOB )
        elif ( result == STATUS_FAILURE_PROCESSING_JOB ) :
          server_pull.complete_job( id, error_code = server.status.JSONStatus.FAILURE_PROCESSING_JOB )

      ping  = 0

    else :
      if ( ( ping > 0 ) and ( ( ping % server_pull_ping ) == 0 ) ) :
        share.sys.log.info( 'polled queue %d times ... no jobs', server_pull_ping ) 

      ping += 1

    if ( term ) :
      share.sys.log.info( 'handled SIGABRT or SIGTERM: terminating' ) ; return

    time.sleep( server_pull_wait )

if ( __name__ == '__main__' ) :
  try :
    share.sys.init()

    if   ( share.sys.conf.get( 'type', section = 'sys' ) == 'acquire' ) :
      pass
    elif ( share.sys.conf.get( 'type', section = 'sys' ) == 'analyse' ) :
      pass
    else :
      raise share.exception.ConfigurationException()

    if   ( share.sys.conf.get( 'mode', section = 'sys' ) == 'cli'     ) :
      do_cli()
    elif ( share.sys.conf.get( 'mode', section = 'sys' ) == 'api'     ) :
      do_api()
    else :
      raise share.exception.ConfigurationException()

  except Exception as e :
    raise e
