# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share

import json, jsonschema, os, sys, tempfile

SCHEMA_CONF = {
  'type' : 'object', 'default' : {}, 'properties' : {
    'path:git'              : { 'type' : 'string', 'default' : tempfile.tempdir },
    'path:job'              : { 'type' : 'string', 'default' : tempfile.tempdir },
    'path:log'              : { 'type' : 'string', 'default' : tempfile.tempdir },
  
    'timeout:extern'        : { 'type' : 'number', 'default' :               60 },
    'timeout:kernel'        : { 'type' : 'number', 'default' :                1 },
  
    'job:manifest-file'     : { 'type' : 'string'                               },
    'job:manifest-data'     : { 'type' : 'string'                               },

    'job:device-db'         : { 'type' : 'object', 'default' : {}, 'patternProperties' : {
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

SCHEMA_JOB  = {
  # core
  'type' : 'object', 'default' : {}, 'properties' : {
    'version'               : { 'type' :  'string'                 },
    'id'                    : { 'type' :  'string'                 },

    'driver-id'             : { 'type' :  'string'                 },
    'driver-spec'           : { 'type' :  'object', 'default' : {} },

    'device-id'             : { 'type' :  'string'                 },
      
    'repo-id'               : { 'type' :  'string'                 },
    'repo-spec'             : { 'type' :  'object', 'default' : {} },
    'depo-id'               : { 'type' :  'string'                 },
    'depo-spec'             : { 'type' :  'object', 'default' : {} },
      
    'trace-period-id'       : { 'type' :  'string', 'default' :   'auto', 'enum' : [ 'auto', 'interval', 'frequency', 'duration' ] },
    'trace-period-spec'     : { 'type' :  'number', 'default' :        0                                                           },
    'trace-resolution-id'   : { 'type' :  'string', 'default' :   'auto', 'enum' : [ 'auto', 'bit'                               ] },
    'trace-resolution-spec' : { 'type' :  'number', 'default' :        0                                                           },

    'trace-count'           : { 'type' :  'number', 'default' :        1                                                           },
    'trace-format'          : { 'type' :  'string', 'default' : 'pickle', 'enum' : [ 'pickle', 'trs'                             ] },
    'trace-crop'            : { 'type' : 'boolean', 'default' :    False                                                           }
  },
  'required' : [ 'version', 'id', 'repo-id', 'repo-spec', 'depo-id', 'depo-spec', 'driver-id', 'driver-spec', 'device-id', 'trace-period-id', 'trace-period-spec', 'trace-resolution-id', 'trace-resolution-spec', 'trace-count', 'trace-format', 'trace-crop' ],
  # options: board
  'oneOf' : [ { 
    'properties' : {
      'board-id'   : { 'enum' : [ 'scale/lpc1313fbd48' ] },
      'board-spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
                'connect-timeout' : { 'type' :     'number', 'default' : 10       },
                'connect-id'      : { 'type' :     'string'                       }
      }, 'required' : [ 'board-id', 'board-spec' ] }
    }
  } ],
  # options: scope
  'oneOf' : [ { 
    'properties' : {
      'scope-id'   : { 'enum' : [ 'picoscope/ps2206b' ] },
      'scope-spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
                'connect-timeout' : { 'type' :     'number', 'default' : 10000    },
                'connect-id'      : { 'type' :     'string'                       },
        'channel-trigger-id'      : { 'enum' : [ 'A', 'B' ], 'default' : 'A'      },
        'channel-acquire-id'      : { 'enum' : [ 'A', 'B' ], 'default' : 'B'      }
      }, 'required' : [ 'scope-id', 'scope-spec' ] }
    }
  } ],
  # options: repo
  'oneOf' : [ { 
    'properties' : {
      'repo-id'   : { 'enum' : [ 'git' ] },
      'repo-spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
        'url'                     : { 'type' :     'string'                       },
        'tag'                     : { 'type' :     'string', 'default' : 'master' }
      }, 'required' : [ 'url', 'tag' ] }
    }
  } ],
  # options: depo
  'oneOf' : [ { 
    'properties' : {
      'depo-id'   : { 'enum' : [ 's3' ] },
      'depo-spec' : { 'type' : 'object', 'default' : {}, 'properties' : {  
        'access-key-id'           : { 'type' :     'string'                       },
        'access-key'              : { 'type' :     'string'                       },
      
        'region-id'               : { 'type' :     'string'                       },
        'bucket-id'               : { 'type' :     'string'                       },

        'verify'                  : { 'type' :    'boolean', 'default' : True     }
      }, 'required' : [ 'access-key', 'access-key-id', 'bucket-id', 'region-id', 'verify' ] }
    }
  } ]
}

def validate( conf, schema ) :
  def defaults( validator_class ) :
    validate_properties = validator_class.VALIDATORS[ 'properties' ]
  
    def set_defaults( validator, properties, instance, schema ):
      for ( property, subschema ) in properties.items() :
        if ( 'default' in subschema ) :
          instance.setdefault( property, subschema[ 'default' ] )
  
      for error in validate_properties( validator, properties, instance, schema ):
        yield error
  
    return jsonschema.validators.extend( validator_class, { 'properties' : set_defaults } )

  validator = defaults( jsonschema.Draft4Validator ) ; validator( schema ).validate( conf )
