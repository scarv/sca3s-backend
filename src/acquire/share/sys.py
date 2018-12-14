# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share

import argparse, json, os, sys, tempfile

conf = None
log  = None

def init() :
  global conf, log

  # parse command line arguments

  parser = argparse.ArgumentParser( add_help = False )
  
  parser.add_argument( '--sys:help',          action =    'help'                                                                                  )
  parser.add_argument( '--sys:version',       action = 'version',                                version = share.version.VERSION                  )
  parser.add_argument( '--sys:debug',         action =   'count',                                default = 0                                      )

  parser.add_argument( '--sys:conf',          action =   'store',                                default = os.path.expandvars( '${HOME}/.scarv' ) )
  parser.add_argument( '--sys:mode',          action =   'store', choices = [ 'cli', 'server' ], default = 'cli'                                  )

  parser.add_argument( '--path:git',          action =   'store', type = str )
  parser.add_argument( '--path:job',          action =   'store', type = str )
  parser.add_argument( '--path:log',          action =   'store', type = str )

  parser.add_argument( '--timeout:extern',    action =   'store', type = int )
  parser.add_argument( '--timeout:kernel',    action =   'store', type = int )

  parser.add_argument( '--job:device-db',     action =   'store', type = str )

  parser.add_argument( '--job:manifest-file', action =   'store', type = str )
  parser.add_argument( '--job:manifest-json', action =   'store', type = str )

  args = { key.replace( '_', '-' ) : value for ( key, value ) in vars( parser.parse_args() ).items() if ( value != None ) }

  # initialise system configuration

  conf = share.conf.Conf()

  conf.populate( args[ 'sys:conf' ] )
  conf.populate( args               )

  schema = {
    'type' : 'object', 'default' : {}, 'properties' : {
      'path:git'          : { 'type' : 'string', 'default' : tempfile.tempdir },
      'path:job'          : { 'type' : 'string', 'default' : tempfile.tempdir },
      'path:log'          : { 'type' : 'string', 'default' : tempfile.tempdir },
  
      'timeout:extern'    : { 'type' : 'number', 'default' :               60 },
      'timeout:kernel'    : { 'type' : 'number', 'default' :                1 },
  
      'job:device-db'     : { 'type' : 'object'                               },

      'job:manifest-file' : { 'type' : 'string'                               },
      'job:manifest-data' : { 'type' : 'string'                               }
    }                              
  }

  share.conf.validate( conf, schema )

  # initialise system logger

  log  = share.log.build_log_sys()
