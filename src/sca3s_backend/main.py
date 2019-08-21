# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

import sca3s_backend as be
import sca3s_spec    as spec

import flask, importlib, os, queue, shutil, signal, tempfile, threading, time

STATUS_SUCCESS                = 0

STATUS_FAILURE_VALIDATING_JOB = 1
STATUS_FAILURE_ALLOCATING_JOB = 2
STATUS_FAILURE_PROCESSING_JOB = 3

def process( manifest ) :
  id = None ; result = STATUS_SUCCESS

  try :
    be.share.sys.log.info( '|> validating job' )
  
    try :
      db = be.share.sys.conf.get( 'device-db', section = 'job' )
    
      if ( manifest.has( 'device-id' ) ) :
        t =  manifest.get( 'device-id' )
    
        if ( db.has( t ) ) :
          for ( key, value ) in db.get( t ).items() :
            manifest.put( key, value )
        else :
          raise be.share.exception.ConfigurationException()
    
      spec.share.schema.validate( manifest, task_spec.schema.MANIFEST )
  
    except Exception as e :
      result = STATUS_FAILURE_VALIDATING_JOB ; raise e

    be.share.sys.log.info( '|< validating job' )

    be.share.sys.log.info( '|> allocating job' )

    try :
      id = manifest.get( 'id' ) ; 

      path = tempfile.mkdtemp( prefix = id + '.', dir = be.share.sys.conf.get( 'job', section = 'path' ) )
      os.chdir( path ) 
      log = be.share.log.build_log_job( name = id, replace = { path : '${JOB}', os.path.basename( path ) : '${JOB}' } )
      job = task_be.job.JobImp( manifest, path, log )

    except Exception as e :
      result = STATUS_FAILURE_ALLOCATING_JOB ; raise e

    be.share.sys.log.info( '|< allocating job' )

    be.share.sys.log.info( '|> processing job' )

    try :    
      job.process_prologue()
      job.process()
      job.process_epilogue()
  
    except Exception as e :
      result = STATUS_FAILURE_PROCESSING_JOB ; raise e

    if ( be.share.sys.conf.get( 'clean', section = 'job' ) ) :
      shutil.rmtree( path, ignore_errors = True )

    be.share.sys.log.info( '|< processing job' )

  except Exception as e :
    be.share.exception.dump( e, log = be.share.sys.log )

  return ( id, result )

def run_mode_cli() :
  if   ( be.share.sys.conf.has( 'manifest-file', section = 'job' ) ) :
    manifest = be.share.conf.Conf( conf = be.share.sys.conf.get( 'manifest-file', section = 'job' ) )
  elif ( be.share.sys.conf.has( 'manifest-data', section = 'job' ) ) :
    manifest = be.share.conf.Conf( conf = be.share.sys.conf.get( 'manifest-data', section = 'job' ) )
  else :
    raise be.share.exception.ConfigurationException()

  process( manifest )

def run_mode_api() :
  pass

#  server_pull      = server.remote.Remote()
#      
#  server_pull_wait = int( be.share.sys.conf.get( 'wait', section = 'server-pull' ) )
#  server_pull_ping = int( be.share.sys.conf.get( 'ping', section = 'server-pull' ) )
#
#  term = False ; ping = 0 ; db = list( be.share.sys.conf.get( 'device-db', section = 'job' ).keys() )
#
#  def signalHandler( signum, frame ) :
#    nonlocal term
#
#    if   ( signum == signal.SIGABRT ) :
#      term = True
#    elif ( signum == signal.SIGTERM ) :
#      term = True
#
#    return
#
#  signal.signal( signal.SIGABRT, signalHandler )
#  signal.signal( signal.SIGTERM, signalHandler )
#
#  while( True ) :
#    manifest = server_pull.receive_job( db )
#  
#    if ( manifest != None ) :
#      ( id, result ) = process( be.share.conf.Conf( conf = manifest ) )
#
#      if ( id != None ) :
#        if   ( result == STATUS_SUCCESS                ) :
#          server_pull.complete_job( id, error_code = server.status.JSONStatus.SUCCESS                )
#        elif ( result == STATUS_FAILURE_VALIDATING_JOB ) :
#          server_pull.complete_job( id, error_code = server.status.JSONStatus.FAILURE_VALIDATING_JOB )
#        elif ( result == STATUS_FAILURE_ALLOCATING_JOB ) :
#          server_pull.complete_job( id, error_code = server.status.JSONStatus.FAILURE_ALLOCATING_JOB )
#        elif ( result == STATUS_FAILURE_PROCESSING_JOB ) :
#          server_pull.complete_job( id, error_code = server.status.JSONStatus.FAILURE_PROCESSING_JOB )
#
#      ping  = 0
#
#    else :
#      if ( ( ping > 0 ) and ( ( ping % server_pull_ping ) == 0 ) ) :
#        be.share.sys.log.info( 'polled queue %d times ... no jobs', server_pull_ping ) 
#
#      ping += 1
#
#    if ( term ) :
#      be.share.sys.log.info( 'handled SIGABRT or SIGTERM: terminating' ) ; return
#
#    time.sleep( server_pull_wait )

if ( __name__ == '__main__' ) :
  try :
    be.share.sys.init()

    if   ( be.share.sys.conf.get( 'task', section = 'sys' ) == 'acquire' ) :
      task_be   = importlib.import_module( 'sca3s_backend.acquire' )
      task_spec = importlib.import_module( 'sca3s_spec.acquire' )
    elif ( be.share.sys.conf.get( 'task', section = 'sys' ) == 'analyse' ) :
      task_be   = importlib.import_module( 'sca3s_backend.analyse' )
      task_spec = importlib.import_module( 'sca3s_spec.analyse' )
    else :
      raise be.share.exception.ConfigurationException()

    if   ( be.share.sys.conf.get( 'mode', section = 'sys' ) == 'cli'     ) :
      run_mode_cli()
    elif ( be.share.sys.conf.get( 'mode', section = 'sys' ) == 'api'     ) :
      run_mode_api()
    else :
      raise be.share.exception.ConfigurationException()

  except Exception as e :
    raise e
