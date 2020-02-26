# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import importlib, multiprocessing, os, shutil, signal, tempfile, time

def process( manifest ) :
  id = None ; status = sca3s_mw.share.status.Status.SUCCESS

  try :
    sca3s_be.share.sys.log.info( 'process job: prologue' )

    try :
      if ( manifest.has(    'job_id' ) ) :
        id = manifest.get( 'job_id' )
      else :
        raise Exception( 'job manifest has no identifier' )

      db = sca3s_be.share.sys.conf.get( 'device_db', section = 'job' )
    
      if ( manifest.has( 'device_id' ) ) :
        t =  manifest.get( 'device_id' )
    
        if ( db.has( t ) ) :
          for ( key, value ) in db.get( t ).items() :
            manifest.put( key, value )

        else :
          raise Exception( 'device database has no such device identifier' )
    
      sca3s_mw.share.schema.validate( manifest, task_mw.schema.MANIFEST_REQ )

      path = tempfile.mkdtemp( prefix = id + '.', dir = sca3s_be.share.sys.conf.get( 'job', section = 'path' ) )
      log  = sca3s_be.share.log.build_log( sca3s_be.share.log.TYPE_JOB, path = path, id = id, replace = { path : '${JOB}', os.path.basename( path ) : '${JOB}' } )
      job  = task_be.job.JobImp( manifest, path, log )

    except Exception as e :
      status = sca3s_mw.share.status.Status.FAILURE_BE_JOB_PROLOGUE ; raise e

    sca3s_be.share.sys.log.info( 'process job: process'  )

    try :    
      job.process_prologue()
      job.process()
  
    except Exception as e :
      status = sca3s_mw.share.status.Status.FAILURE_BE_JOB_PROCESS  ; raise e

    finally :
      job.process_epilogue()

    sca3s_be.share.sys.log.info( 'process job: epilogue' )

    try :    
      if ( sca3s_be.share.sys.conf.get( 'clean', section = 'job' ) ) :
        shutil.rmtree( path, ignore_errors = True )

    except Exception as e :
      status = sca3s_mw.share.status.Status.FAILURE_BE_JOB_EPILOGUE ; raise e

  except Exception as e :
    sca3s_mw.share.exception.dump( e, log = sca3s_be.share.sys.log )

  return ( id, status )

def run_mode_cli() :
  if   ( sca3s_be.share.sys.conf.has( 'manifest_file', section = 'job' ) ) :
    manifest = sca3s_be.share.conf.Conf( conf = sca3s_be.share.sys.conf.get( 'manifest_file', section = 'job' ) )
  elif ( sca3s_be.share.sys.conf.has( 'manifest_data', section = 'job' ) ) :
    manifest = sca3s_be.share.conf.Conf( conf = sca3s_be.share.sys.conf.get( 'manifest_data', section = 'job' ) )
  else :
    raise Exception( 'undefined manifest' )

  process( manifest )

def run_mode_api() :
  api               = task_be.api.APIImp()
      
  api_announce_wait = int( sca3s_be.share.sys.conf.get( 'announce_wait', section = 'api' ) )
  api_announce_ping = int( sca3s_be.share.sys.conf.get( 'announce_ping', section = 'api' ) )
  api_retrieve_wait = int( sca3s_be.share.sys.conf.get( 'retrieve_wait', section = 'api' ) )
  api_retrieve_ping = int( sca3s_be.share.sys.conf.get( 'retrieve_ping', section = 'api' ) )

  api_term          = False 

  def signalHandler( signum, frame ) :
    nonlocal api_term

    if   ( signum == signal.SIGABRT ) :
      api_term = True
    elif ( signum == signal.SIGTERM ) :
      api_term = True

    return

  signal.signal( signal.SIGABRT, signalHandler )
  signal.signal( signal.SIGTERM, signalHandler )

  def announceHandler() :
    ping = 0

    while( True ) :
      try :
        api.announce()

        if ( api_term ) :
          sca3s_be.share.sys.log.info( 'handled SIGABRT or SIGTERM: terminating' ) ; return

        if ( ( ping % api_announce_ping ) == 0 ) :
          sca3s_be.share.sys.log.info( 'activity ping: announce thread' )

        ping += 1 ; time.sleep( api_announce_wait )

      except Exception as e :
        sca3s_mw.share.exception.dump( e, log = sca3s_be.share.sys.log )
    
  def retrieveHandler() :
    ping = 0 ; 
  
    while( True ) :
      try :
        manifest = api.retrieve()
    
        if ( manifest != None ) :
          ( id, status ) = process( sca3s_be.share.conf.Conf( conf = manifest ) )
  
          if ( id != None ) :
            api.complete( id, status = status )
    
        if ( api_term ) :
          sca3s_be.share.sys.log.info( 'handled SIGABRT or SIGTERM: terminating' ) ; return

        if ( ( ping % api_retrieve_ping ) == 0 ) :
          sca3s_be.share.sys.log.info( 'activity ping: retrieve thread' )
    
        ping += 1 ; time.sleep( api_retrieve_wait )
  
      except Exception as e :
        sca3s_mw.share.exception.dump( e, log = sca3s_be.share.sys.log )

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
      raise Exception( 'unknown task' )

    if   ( sca3s_be.share.sys.conf.get( 'mode', section = 'sys' ) == 'cli'     ) :
      run_mode_cli()
    elif ( sca3s_be.share.sys.conf.get( 'mode', section = 'sys' ) == 'api'     ) :
      run_mode_api()
    else :
      raise Exception( 'unknown mode' )

  except Exception as e :
    raise e
