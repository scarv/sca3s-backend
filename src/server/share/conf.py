# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share

from acquire import board  as board
from acquire import scope  as scope
from acquire import driver as driver

from acquire import repo   as repo
from acquire import depo   as depo

import json, jsonschema, os, sys, tempfile

SCHEMA = {
  'type' : 'object', 'default' : {}, 'properties' : {
    'path:git'              : { 'type' :  'string', 'default' : tempfile.tempdir },
    'path:job'              : { 'type' :  'string', 'default' : tempfile.tempdir },
    'path:log'              : { 'type' :  'string', 'default' : tempfile.tempdir },

    'security:creds'        : { 'type' :  'object', 'default' : {}               },

    'security:diff-url'     : { 'type' :  'string', 'default' : 'git@scarv_sca3s-target:scarv/sca3s-target.git' },
    'security:diff-pattern' : { 'type' :  'string', 'default' : 'README.md|src/kernel/.*'                       },

    'server-push:host'      : { 'type' :  'string', 'default' :      '127.0.0.1' },
    'server-push:port'      : { 'type' :  'number', 'default' :             1234 },

    'server-pull:wait'      : { 'type' :  'number', 'default' :               60 },
    'server-pull:ping'      : { 'type' :  'number', 'default' :               10 },

    'run:env'               : { 'type' :  'object', 'default' : {}               },
    'run:timeout'           : { 'type' :  'number', 'default' :               60 },
  
    'job:timeout'           : { 'type' :  'number', 'default' :                1 },

    'job:manifest-file'     : { 'type' :  'string'                               },
    'job:manifest-data'     : { 'type' :  'string'                               },

    'job:clean'             : { 'type' : 'boolean', 'default' : False            },

    'job:device-db'         : { 'type' :  'object', 'default' : {}, 'patternProperties' : {
      '^.*$' : { 'type' : 'object', 'default' : {}, 'properties' : {
        'board-desc' : { 'type' : 'string' },
        'board-id'   : { 'type' : 'string' },
        'board-spec' : { 'type' : 'object' },

        'scope-desc' : { 'type' : 'string' },
        'scope-id'   : { 'type' : 'string' },
        'scope-spec' : { 'type' : 'object' }
      }, 'required' : [ 'board-desc', 'board-id', 'board-spec', 'scope-desc', 'scope-id', 'scope-spec' ] }
    } }
  }
}

class Conf( dict ) :
  def __init__( self, conf = None ) :
    super().__init__()

    if ( conf != None ) :
      self.populate( conf )

  def has( self, key,        section = None               ) :
    if ( section != None ) :
      key = section + ':' + key

    return ( key in self )

  def get( self, key,        section = None, value = None ) :
    if ( section != None ) :
      key = section + ':' + key
  
    return self[ key ] if ( key in self ) else value
  
  def put( self, key, value, section = None               ) :
    if ( section != None ) :
      key = section + ':' + key
  
    self[ key ] = value

  def keys( self, section = None ) :
    r = list()

    for key in super().keys() :
      if ( ( section == None ) or ( key.startswith( section + ':' ) ) ) :
        r.append( key )

    return r

  def populate( self, x ) :
    if   ( isinstance( x, dict ) ) :
                              self.update(             x    )
    elif ( isinstance( x, str  ) ) :
      if ( os.path.isfile( x ) ) :
        fd = open( x, 'r' ) ; self.update( json.load ( fd ) ) ; fd.close()
      else :
                              self.update( json.loads( x  ) )

    for ( key, value ) in self.items() :
      if ( value != None ) :
        if   ( isinstance( value, dict ) ) :
          value = share.conf.Conf( conf = value )
        elif ( isinstance( value, str  ) ) :
          value = os.path.expandvars( value )

      self[ key ] = value
