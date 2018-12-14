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

import flask, queue, threading

app = flask.Flask( __name__ ) ; jobs = queue.Queue( 1 )

def process( manifest ) :
    share.sys.log.info( '|>>>   creating job' )

    job = share.job.Job( manifest )

    share.sys.log.info( '|>>> processing job id = %s' % ( job.id ) )

    job.process_prologue()
    job.process()
    job.process_epilogue()

    share.sys.log.info( '|<<< processing job id = %s' % ( job.id ) )

def server_worker() :
  while( True ) :
    process( share.conf.Conf( conf = jobs.get() ) )

@app.route( '/api/device', methods = [ 'GET', 'POST' ] )
def server_api_device() :
  t = dict()

  for ( key, value ) in share.sys.conf.get( 'device-db', section = 'job' ).items() :
    t[ key ] = { 'board-desc' : value[ 'board-desc' ],
                 'scope-desc' : value[ 'scope-desc' ] }

  return flask.jsonify( t )

@app.route( '/api/submit', methods = [ 'GET', 'POST' ] )
def server_api_submit() :
  try :
    share.sys.log.info( '!>>> queueing job' )

    jobs.put( flask.request.get_json() )

    share.sys.log.info( '!<<< queueing job' )
  except Exception as e :
    raise e

  return ""

if ( __name__ == '__main__' ) :
  try :
    share.sys.init()
  except Exception as e :
    raise e

  try :
    if   ( share.sys.conf.get( 'mode', section = 'sys' ) == 'server' ) :
      threading.Thread( target = server_worker ).start() ; app.run()

    elif ( share.sys.conf.get( 'mode', section = 'sys' ) == 'cli'    ) :
      if   ( share.sys.conf.has( 'manifest-file', section = 'job' ) ) :
        manifest = share.conf.Conf( conf = share.sys.conf.get( 'manifest-file', section = 'job' ) )
      elif ( share.sys.conf.has( 'manifest-data', section = 'job' ) ) :
        manifest = share.conf.Conf( conf = share.sys.conf.get( 'manifest-data', section = 'job' ) )
      else :
        raise Exception()
  
      process( manifest )

  except Exception as e :
    raise e
