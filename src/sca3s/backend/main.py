# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import importlib, os, shutil, signal, tempfile, time

STATUS_SUCCESS                = 0

STATUS_FAILURE_VALIDATING_JOB = 1
STATUS_FAILURE_ALLOCATING_JOB = 2
STATUS_FAILURE_PROCESSING_JOB = 3

def process( manifest ) :
  id = None ; result = STATUS_SUCCESS

  try :
    sca3s_be.share.sys.log.info( 'validating job' )
  
    try :
      if ( manifest.has(    'job_id' ) ) :
        id = manifest.get( 'job_id' )
      else :
        raise sca3s_be.share.exception.BackEndException( message = sca3s_mw.share.status.INVALID_CONF )

      db = sca3s_be.share.sys.conf.get( 'device_db', section = 'job' )
    
      if ( manifest.has( 'device_id' ) ) :
        t =  manifest.get( 'device_id' )
    
        if ( db.has( t ) ) :
          for ( key, value ) in db.get( t ).items() :
            manifest.put( key, value )

        else :
          raise sca3s_be.share.exception.BackEndException( message = sca3s_mw.share.status.INVALID_CONF )
    
      sca3s_mw.share.schema.validate( manifest, task_mw.schema.SCHEMA_MANIFEST )
  
    except Exception as e :
      result = STATUS_FAILURE_VALIDATING_JOB ; raise e

    sca3s_be.share.sys.log.info( 'allocating job' )

    try :
      path = tempfile.mkdtemp( prefix = id + '.', dir = sca3s_be.share.sys.conf.get( 'job', section = 'path' ) )
      log  = sca3s_be.share.log.build_log( sca3s_be.share.log.TYPE_JOB, path = path, id = id, replace = { path : '${JOB}', os.path.basename( path ) : '${JOB}' } )

      job  = task_be.job.JobImp( manifest, path, log )

    except Exception as e :
      result = STATUS_FAILURE_ALLOCATING_JOB ; raise e

    sca3s_be.share.sys.log.info( 'processing job' )

    try :    
      job.process_prologue()
      job.process()
  
    except Exception as e :
      result = STATUS_FAILURE_PROCESSING_JOB ; raise e

    finally :
      job.process_epilogue()

    if ( sca3s_be.share.sys.conf.get( 'clean', section = 'job' ) ) :
      shutil.rmtree( path, ignore_errors = True )

  except Exception as e :
    sca3s_be.share.exception.dump( e, log = sca3s_be.share.sys.log )

  return ( id, result )

def run_mode_cli() :
  if   ( sca3s_be.share.sys.conf.has( 'manifest_file', section = 'job' ) ) :
    manifest = sca3s_be.share.conf.Conf( conf = sca3s_be.share.sys.conf.get( 'manifest_file', section = 'job' ) )
  elif ( sca3s_be.share.sys.conf.has( 'manifest_data', section = 'job' ) ) :
    manifest = sca3s_be.share.conf.Conf( conf = sca3s_be.share.sys.conf.get( 'manifest_data', section = 'job' ) )
  else :
    raise sca3s_be.share.exception.BackEndException( message = sca3s_mw.share.status.INVALID_CONF )

  process( manifest )

def run_mode_api() :
  api      = task_be.api.APIImp()
      
  api_wait = int( sca3s_be.share.sys.conf.get( 'wait', section = 'api' ) )
  api_ping = int( sca3s_be.share.sys.conf.get( 'ping', section = 'api' ) )

  ping = 0 ; term = False 

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
    try :
      manifest = api.retrieve_job()
  
      if ( manifest == None ) :
        ping += 1

        if ( ( ping % api_ping ) == 0 ) :
          sca3s_be.share.sys.log.info( 'polled queue %d times ... no jobs', api_ping ) 
      
      else :  
        ping  = 0

        ( id, result ) = process( sca3s_be.share.conf.Conf( conf = manifest ) )

        if ( id != None ) :
          if   ( result == STATUS_SUCCESS                ) :
            api.complete_job( id, error_code = task_be.api.JSONStatus.SUCCESS                )
          elif ( result == STATUS_FAILURE_VALIDATING_JOB ) :
            api.complete_job( id, error_code = task_be.api.JSONStatus.FAILURE_VALIDATING_JOB )
          elif ( result == STATUS_FAILURE_ALLOCATING_JOB ) :
            api.complete_job( id, error_code = task_be.api.JSONStatus.FAILURE_ALLOCATING_JOB )
          elif ( result == STATUS_FAILURE_PROCESSING_JOB ) :
            api.complete_job( id, error_code = task_be.api.JSONStatus.FAILURE_PROCESSING_JOB )
  
      if ( term ) :
        sca3s_be.share.sys.log.info( 'handled SIGABRT or SIGTERM: terminating' ) ; return
  
      time.sleep( api_wait )

    except Exception as e :
      sca3s_be.share.exception.dump( e, log = sca3s_be.share.sys.log )

if ( __name__ == '__main__' ) :
  try :
    sca3s_be.share.sys.init()

    if   ( sca3s_be.share.sys.conf.get( 'task', section = 'sys' ) == 'acquire' ) :
      task_be = importlib.import_module( 'sca3s.backend.acquire' )
      task_mw = importlib.import_module( 'sca3s.middleware.acquire' )
    elif ( sca3s_be.share.sys.conf.get( 'task', section = 'sys' ) == 'analyse' ) :
      task_be = importlib.import_module( 'sca3s.backend.analyse' )
      task_mw = importlib.import_module( 'sca3s.middleware.analyse' )
    else :
      raise sca3s_be.share.exception.BackEndException( message = sca3s_mw.share.status.INVALID_CONF )

    if   ( sca3s_be.share.sys.conf.get( 'mode', section = 'sys' ) == 'cli'     ) :
      run_mode_cli()
    elif ( sca3s_be.share.sys.conf.get( 'mode', section = 'sys' ) == 'api'     ) :
      run_mode_api()
    else :
      raise sca3s_be.share.exception.BackEndException( message = sca3s_mw.share.status.INVALID_CONF )

  except Exception as e :
    raise e
