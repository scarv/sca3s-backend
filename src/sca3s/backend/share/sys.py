# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend as be
from sca3s import spec    as spec

import argparse, logging, os, sys

conf = None
log  = None

def init() :
  global conf, log



  print( 'dump env  = {0}'.format( os.environ      ) ) 

  print( 'dump argc = {0}'.format( len( sys.argv ) ) )
  print( 'dump argv = {0}'.format(      sys.argv   ) )



  # parse command line arguments

  parser = argparse.ArgumentParser( add_help = False )
  
  parser.add_argument( '--sys:help',          action =    'help'                                                                         )
  parser.add_argument( '--sys:version',       action = 'version',                                     version = be.share.version.VERSION )
  parser.add_argument( '--sys:debug',         action =   'count',                                     default = 0                        )

  parser.add_argument( '--sys:conf',          action =   'store', type = str )

  parser.add_argument( '--sys:task',          action =   'store', choices = [ 'acquire', 'analyse' ], default = 'acquire'                )
  parser.add_argument( '--sys:mode',          action =   'store', choices = [ 'cli', 'api'         ], default = 'cli'                    )

  parser.add_argument( '--path:git',          action =   'store', type = str )
  parser.add_argument( '--path:job',          action =   'store', type = str )
  parser.add_argument( '--path:log',          action =   'store', type = str )

  parser.add_argument( '--job:device-db',     action =   'store', type = str )

  parser.add_argument( '--job:manifest-file', action =   'store', type = str )
  parser.add_argument( '--job:manifest-json', action =   'store', type = str )

  args = { key.replace( '_', '-' ) : value for ( key, value ) in vars( parser.parse_args() ).items() if ( value != None ) }

  # initialise system configuration, from configuration file *then* command line arguments

  conf = be.share.conf.Conf()



  
  print( 'sys:conf' in args )
  print( args[ 'sys:conf' ] )
  print( os.path.isfile( args[ 'sys:conf' ] ) )




  if ( ( 'sys:conf' in args ) and ( os.path.isfile( args[ 'sys:conf' ] ) ) ) :
    conf.populate( args[ 'sys:conf' ] )
  else :
    raise Exception()

  conf.populate( args )

  spec.share.schema.validate( conf, be.share.conf.SCHEMA_CONF )

  # initialise system logger

  log  = be.share.log.build_log( be.share.log.TYPE_SYS, path = be.share.sys.conf.get( 'log', section = 'path' ) )

  # dump 

  log.debug( 'dump env  = {0}'.format( os.environ      ) ) 

  log.debug( 'dump argc = {0}'.format( len( sys.argv ) ) )
  log.debug( 'dump argv = {0}'.format(      sys.argv   ) )

  log.indent_inc( message = 'dump sys configuration', level = logging.DEBUG )
  conf.dump( log, level = logging.DEBUG )
  log.indent_dec()  
