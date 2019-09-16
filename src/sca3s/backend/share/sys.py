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

  # parse command line arguments

  parser = argparse.ArgumentParser( add_help = False )
  
  parser.add_argument( '--sys:help',          action =    'help'                                                                         )
  parser.add_argument( '--sys:version',       action = 'version',                                     version = be.share.version.VERSION )
  parser.add_argument( '--sys:debug',         action =   'count',                                     default = 0                        )

  parser.add_argument( '--sys:conf',          action =   'store', type = str )

  parser.add_argument( '--sys:task',          action =   'store', choices = [ 'acquire', 'analyse' ], default = 'acquire'                )
  parser.add_argument( '--sys:mode',          action =   'store', choices = [ 'cli', 'api'         ], default = 'cli'                    )

  parser.add_argument( '--sys:volume',        action =  'append', type = str,                         default = list()                   )

  parser.add_argument( '--job:manifest-file', action =   'store', type = str )
  parser.add_argument( '--job:manifest-json', action =   'store', type = str )

  args = { key.replace( '_', '-' ) : value for ( key, value ) in vars( parser.parse_args() ).items() if ( value != None ) }

  # initialise system configuration, from configuration file *then* command line arguments

  conf = be.share.conf.Conf()

  if ( ( 'sys:conf' in args ) and ( os.path.isfile( args[ 'sys:conf' ] ) ) ) :
    conf.populate( args[ 'sys:conf' ] )

  conf.populate( args )

  spec.share.schema.validate( conf, be.share.conf.SCHEMA_CONF )

  # initialise system logger

  log  = be.share.log.build_log( be.share.log.TYPE_SYS, path = be.share.sys.conf.get( 'log', section = 'path' ) )

  # dump configuration

  log.indent_inc( message = 'dump env configuration', level = logging.DEBUG )

  log.debug( 'env    = {0}'.format( os.environ      ) ) 

  log.debug( 'argc   = {0}'.format( len( sys.argv ) ) )
  log.debug( 'argv   = {0}'.format(      sys.argv   ) )

  log.debug( 'cwd    = {0}'.format( os.getcwd()     ) )

  log.debug( 'uid    = {0} => {1}'.format( os.getuid(), os.geteuid() ) )
  log.debug( 'gid    = {0} => {1}'.format( os.getgid(), os.getegid() ) )

  log.debug( 'groups = {0}'.format( os.getgroups()  ) )

  log.indent_dec()  

  log.indent_inc( message = 'dump sys configuration', level = logging.DEBUG )
  conf.dump( log, level = logging.DEBUG )
  log.indent_dec()  
