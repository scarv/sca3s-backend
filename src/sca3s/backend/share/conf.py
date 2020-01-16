# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import json, jsonschema, logging, os, sys, tempfile

SCHEMA_CONF = {
  'type' : 'object', 'default' : {}, 'properties' : {
    'path:job'          : { 'type' :  'string',         'default' : tempfile.tempdir },
    'path:log'          : { 'type' :  'string',         'default' : tempfile.tempdir },

    'security:creds'    : { 'type' :  'object',         'default' : {}               },

    'security:template' : { 'type' :  'object',         'default' : {}, 'patternProperties' : {
          'url' : { 'type' :  'string', 'default' : 'git@github.com/scarv/sca3s-harness.git' },
          'tag' : { 'type' :  'string', 'default' : 'master'                                 },
      'pattern' : { 'type' :  'string', 'default' : 'README.md|src/kernel/.*'                }
    } },

    'api:instance'      : { 'enum' : [ '1', '2', '*' ], 'default' :                     '*' },
    'api:url'           : { 'type' :  'string',         'default' : 'https://lab.scarv.org' },

    'api:retry_wait'    : { 'type' :  'number',         'default' :                       3 },
    'api:retry_count'   : { 'type' :  'number',         'default' :                       3 },

    'api:announce_wait' : { 'type' :  'number',         'default' :                     600 },
    'api:announce_ping' : { 'type' :  'number',         'default' :                       1 },
    'api:retrieve_wait' : { 'type' :  'number',         'default' :                      30 },
    'api:retrieve_ping' : { 'type' :  'number',         'default' :                      10 },

    'run:env'           : { 'type' :  'object',         'default' :                      {} },
    'run:timeout'       : { 'type' :  'number',         'default' :                      60 },
  
    'job:timeout'       : { 'type' :  'number',         'default' :                       1 },

    'job:manifest_file' : { 'type' :  'string'                                              },
    'job:manifest_data' : { 'type' :  'string'                                              },

    'job:clean'         : { 'type' : 'boolean',         'default' :                   False },

    'job:device_db'     : { 'type' :  'object',         'default' : {}, 'patternProperties' : {
      '^.*$' : { 'type' : 'object', 'default' : {}, 'properties' : {
        'board_id'   : { 'type' : 'string' },
        'board_desc' : { 'type' : 'string' },
        'board_spec' : { 'type' : 'object' },
        'board_path' : { 'type' :  'array', 'items' : { 'type' : 'string' } },

        'scope_id'   : { 'type' : 'string' },
        'scope_desc' : { 'type' : 'string' },
        'scope_spec' : { 'type' : 'object' },
        'scope_path' : { 'type' :  'array', 'items' : { 'type' : 'string' } }
      }, 'required' : [ 'board_id', 'board_desc', 'board_spec', 'scope_id', 'scope_desc', 'scope_spec' ] }
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
          value = sca3s_be.share.conf.Conf( conf = value )
        elif ( isinstance( value, str  ) ) :
          value = os.path.expandvars( value )

      self[ key ] = value

  def dump( self, logger, level = logging.INFO ) :
    n = 0

    for ( key, value ) in sorted( self.items() ) : 
      n = max( n, len( key ) )

    for ( key, value ) in sorted( self.items() ) :
      logger.log( level, '{0:<{width}} = {1}'.format( key, json.dumps( value ), width = n ) )
