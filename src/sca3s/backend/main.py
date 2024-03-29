# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import importlib, multiprocessing, os, shutil, signal, tempfile, time

def process( manifest ) :
  job_id = None ; job_status = sca3s_mw.share.status.Status.SUCCESS ; job_response = dict()

  try :
    sca3s_be.share.sys.log.info( 'process job prologue' )

    try :
      if ( not manifest.has( 'job_id'      ) ) :
        raise Exception( 'manifest missing job identifier' )
      else :
        job_id      = manifest.get( 'job_id'      )

      if ( not manifest.has( 'job_type'    ) ) :
        raise Exception( 'manifest missing job type'       )
      else :
        job_type    = manifest.get( 'job_type'    )

      if ( not manifest.has( 'job_version' ) ) :
        raise Exception( 'manifest missing job version'    )
      else :
        job_version = manifest.get( 'job_version' )

      if ( not sca3s_be.share.version.match( job_version ) ) :
        raise Exception( 'inconsistent manifest version' )

      db = sca3s_be.share.sys.conf.get( 'device_db', section = 'job' )
    
      if ( manifest.has( 'device_id' ) ) :
        t = manifest.get( 'device_id' )
    
        if ( db.has( t ) ) :
          for ( key, value ) in db.get( t ).items() :
            manifest.put( key, value )

        else :
          raise Exception( 'unsupported device' )

      sca3s_mw.share.schema.validate( task_mw.schema.MANIFEST_REQ, manifest )
      sca3s_mw.share.schema.populate( task_mw.schema.MANIFEST_REQ, manifest )

      path = tempfile.mkdtemp( prefix = job_id + '.', dir = sca3s_be.share.sys.conf.get( 'job', section = 'path' ) )  
      job  = task_be.job.JobImp( manifest, path )

    except Exception as e :
      job_status = sca3s_mw.share.status.Status.FAILURE_BE_JOB_PROLOGUE ; raise e

    sca3s_be.share.sys.relax()

    sca3s_be.share.sys.log.info( 'process job'          )

    try :    
      job.execute_prologue()
      job.execute()
      job.execute_epilogue()

      job_response = job.result_response
  
    except Exception as e :
      job_status = sca3s_mw.share.status.Status.FAILURE_BE_JOB_PROCESS  ; raise e

    sca3s_be.share.sys.relax()

    sca3s_be.share.sys.log.info( 'process job epilogue' )

    try :    
      if ( sca3s_be.share.sys.conf.get( 'clean', section = 'job' ) ) :
        shutil.rmtree( path, ignore_errors = True )

    except Exception as e :
      job_status = sca3s_mw.share.status.Status.FAILURE_BE_JOB_EPILOGUE ; raise e

    sca3s_be.share.sys.relax()

  except Exception as e :
    sca3s_mw.share.exception.dump( e, log = sca3s_be.share.sys.log )

  return ( job_id, job_status, job_response )

# Execute server in API mode: process a manifest which is
#
# 1. read from a specified file, or
# 2. specified directly as immediate data.

def run_mode_cli() :
  if   ( sca3s_be.share.sys.conf.has( 'manifest_file', section = 'job' ) ) :
    manifest = sca3s_be.share.conf.Conf( conf = sca3s_be.share.sys.conf.get( 'manifest_file', section = 'job' ) )
  elif ( sca3s_be.share.sys.conf.has( 'manifest_data', section = 'job' ) ) :
    manifest = sca3s_be.share.conf.Conf( conf = sca3s_be.share.sys.conf.get( 'manifest_data', section = 'job' ) )
  else :
    raise Exception( 'unsupported manifest type' )

  process( manifest )

# Execute server in API mode: execute
#
# 1. a "announce handler" thread: 
#    - make API call; announce the server to   the API
#    - terminate if the signal handler says so
#    - write an activity ping after parameterised number of iterations
#    - back-off, i.e., wait, for parameterised period
#
# 2. a "retrieve handler" thread:
#    - make API call; retrieve job        from the API, process it, and confirm completion
#    - terminate if the signal handler says so
#    - write an activity ping after parameterised number of iterations
#    - back-off, i.e., wait, for parameterised period

def run_mode_api() :
  api               = task_be.api.APIImp()
      
  api_announce_wait = int( sca3s_be.share.sys.conf.get( 'announce_wait', section = 'api' ) )
  api_announce_ping = int( sca3s_be.share.sys.conf.get( 'announce_ping', section = 'api' ) )
  api_retrieve_wait = int( sca3s_be.share.sys.conf.get( 'retrieve_wait', section = 'api' ) )
  api_retrieve_ping = int( sca3s_be.share.sys.conf.get( 'retrieve_ping', section = 'api' ) )

  api_term          = False 

  def   signalHandler( signum, frame ) :
    nonlocal api_term

    if   ( signum == signal.SIGABRT ) :
      api_term = True
    elif ( signum == signal.SIGTERM ) :
      api_term = True

    return

  def announceHandler() :
    ping = 0

    while( True ) :
      try :
        api.announce()

        if (          api_term                 ) :
          sca3s_be.share.sys.log.info( 'announce thread: handled SIG{ABRT,TERM} => terminating' ) ; return
        if ( ( ping % api_announce_ping ) == 0 ) :
          sca3s_be.share.sys.log.info( 'announce thread: activity ping' )
          sca3s_be.share.sys.relax( verbose = True )

        ping += 1 ; time.sleep( api_announce_wait )

      except Exception as e :
        sca3s_mw.share.exception.dump( e, log = sca3s_be.share.sys.log )
    
  def retrieveHandler() :
    ping = 0
  
    while( True ) :
      try :
        manifest = api.retrieve()

        if ( manifest != None ) :
          api.complete( *process( sca3s_be.share.conf.Conf( conf = manifest ) ) )
    
        if (          api_term                 ) :
          sca3s_be.share.sys.log.info( 'retrieve thread: handled SIG{ABRT,TERM} => terminating' ) ; return
        if ( ( ping % api_retrieve_ping ) == 0 ) :
          sca3s_be.share.sys.log.info( 'retrieve thread: activity ping' )
          sca3s_be.share.sys.relax( verbose = True )
    
        ping += 1 ; time.sleep( api_retrieve_wait )
  
      except Exception as e :
        sca3s_mw.share.exception.dump( e, log = sca3s_be.share.sys.log )

  signal.signal( signal.SIGABRT, signalHandler )
  signal.signal( signal.SIGTERM, signalHandler )

  multiprocessing.Process( target = announceHandler ).start() ; retrieveHandler()

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
      raise Exception( 'unsupported server task' )

    if   ( sca3s_be.share.sys.conf.get( 'mode', section = 'sys' ) == 'cli'     ) :
      run_mode_cli()
    elif ( sca3s_be.share.sys.conf.get( 'mode', section = 'sys' ) == 'api'     ) :
      run_mode_api()
    else :
      raise Exception( 'unsupported server mode' )

  except Exception as e :
    raise e
