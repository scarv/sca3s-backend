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

SCHEMA_CONF = {
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

SCHEMA_JOB  = {
  'definitions' : {
     'trace-spec' : { 'type' :  'object', 'default' : {}, 'properties' : {
           'period-id'   : { 'type' :  'string', 'default' : 'auto', 'enum' : [ 'auto', 'interval', 'frequency', 'duration' ] },
           'period-spec' : { 'type' :  'number', 'default' :      0                                                           },
       'resolution-id'   : { 'type' :  'string', 'default' : 'auto', 'enum' : [ 'auto', 'bit'                               ] },
       'resolution-spec' : { 'type' :  'number', 'default' :      0                                                           },
   
       'count'           : { 'type' :  'number', 'default' :      1                                                           },
       'format'          : { 'type' :  'string', 'default' :  'pkl', 'enum' : [ 'pkl', 'csv', 'trs'                         ] },

       'compress'        : { 'type' : 'boolean', 'default' :   True                                                           },
       'crop'            : { 'type' : 'boolean', 'default' :   True                                                           }
    }, 'required' : [] }
  },
  'type' : 'object', 'default' : {}, 'properties' : {
    'version'     : { 'type' :  'string' },
    'id'          : { 'type' :  'string' },

    'remark'      : { 'type' :  'string' },
    'status'      : { 'type' :  'number' },

    'driver-id'   : { 'type' :  'string' },
    'device-id'   : { 'type' :  'string' },
      
      'repo-id'   : { 'type' :  'string' },
      'depo-id'   : { 'type' :  'string' },

     'trace-spec' : { '$ref' : '#/definitions/trace-spec' }
  }, 'required' : [ 'version', 'id', 'repo-id', 'depo-id', 'driver-id', 'device-id', 'trace-spec' ],
  'allOf' : [ {
    'oneOf' : [ { # options: driver-spec
      'properties' : {
        'driver-id'   : { 'enum' : [ 'block/enc' ] },
        'driver-spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
          'verify' : { 'type' : 'boolean', 'default' : True }
        } },
         'trace-spec' : { 
           'allOf' : [ { '$ref' : '#/definitions/trace-spec' }, { 'properties' : { # extend trace-spec w. driver-specific content options
             'content' : { 'type' :   'array', 'default' : [ 'signal', 'm', 'c', 'k' ], 'items' : {
               'enum' : [ 'trigger', 'signal', 'tsc', 'k', 'r', 'm', 'c' ]
            } },
          } } ]
        }
      } 
    }, {
      'properties' : {
        'driver-id'   : { 'enum' : [ 'block/dec' ] },
        'driver-spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
          'verify' : { 'type' : 'boolean', 'default' : True }
        } },
         'trace-spec' : { 
           'allOf' : [ { '$ref' : '#/definitions/trace-spec' }, { 'properties' : { # extend trace-spec w. driver-specific content options
             'content' : { 'type' :   'array', 'default' : [ 'signal', 'c', 'm', 'k' ], 'items' : {
               'enum' : [ 'trigger', 'signal', 'tsc', 'k', 'r', 'm', 'c' ]
            } },
          } } ]
        }
      }
    } ] }, { 
    'oneOf' : [ { # options:  board-spec
      'properties' : {
         'board-id'   : { 'enum' : [ 'scale/lpc1313fbd48' ] },
         'board-spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
                   'connect-id'      : { 'type' : 'string' },
                   'connect-timeout' : { 'type' : 'number' },
  
                   'program-mode'    : { 'enum' : [ 'usb', 'jlink' ] },
                   'program-id'      : { 'type' : 'string' },
                   'program-timeout' : { 'type' : 'number' }
        }, 'required' : [ 'connect-id', 'connect-timeout', 'program-mode', 'program-id', 'program-timeout' ] }
      }
    } ] }, { 
    'oneOf' : [ { # options:  scope-spec
      'properties' : {
         'scope-id'   : { 'enum' : [ 'picoscope/ps2206b' ] },
         'scope-spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
                   'connect-id'      : { 'type' : 'string' },
                   'connect-timeout' : { 'type' : 'number' },

           'channel-trigger-id'      : { 
             'enum' : [ 'A', 'B' ] 
            },
           'channel-acquire-id'      : {
             'enum' : [ 'A', 'B' ]
            },
           'channel-disable-id'      : { 'type' :  'array', 'default' : [], 'items' : {
             'enum' : [ 'A', 'B' ]
           } }
        }, 'required' : [ 'connect-id', 'connect-timeout', 'channel-trigger-id', 'channel-acquire-id' ] }
      }
    }, {
      'properties' : {
         'scope-id'   : { 'enum' : [ 'picoscope/ps3406b' ] },
         'scope-spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
                   'connect-id'      : { 'type' : 'string' },
                   'connect-timeout' : { 'type' : 'number' },
  
           'channel-trigger-id'      : { 
             'enum' : [ 'A', 'B', 'C', 'D' ] 
            },
           'channel-acquire-id'      : {
             'enum' : [ 'A', 'B', 'C', 'D' ]
            },
           'channel-disable-id'      : { 'type' :  'array', 'default' : [], 'items' : {
             'enum' : [ 'A', 'B', 'C', 'D' ]
           } }
        }, 'required' : [ 'connect-id', 'connect-timeout', 'channel-trigger-id', 'channel-acquire-id' ] }
      }
    } ] }, { 
    'oneOf' : [ { # options:   repo-spec
      'properties' : {
          'repo-id'   : { 'enum' : [ 'git' ] },
          'repo-spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
            'url'                     : { 'type' : 'string'                       },
            'tag'                     : { 'type' : 'string', 'default' : 'master' },
            'conf'                    : { 'type' : 'object', 'default' : {}       }
        }, 'required' : [ 'url' ] }
      }
    } ] }, { 
    'oneOf' : [ { # options:   depo-spec
      'properties' : {
          'depo-id'   : { 'enum' : [ 's3' ] },
          'depo-spec' : { 'type' : 'object', 'default' : {}, 'properties' : {  
            'identity_id'             : { 'type' :     'string'                                 },
  
              'region-id'             : { 'type' :     'string', 'default' : 'eu-west-1'        },
              'bucket-id'             : { 'type' :     'string', 'default' : 'scarv-lab-traces' },
  
            'verify'                  : { 'type' :    'boolean', 'default' : True               }
        }, 'required' : [ 'identity_id' ] }
      }
    } ] }
  ]
}

# this is basically the solution to a FAQ in
# 
# https://python-jsonschema.readthedocs.io
#
# which (recursively) applies default values within a schema

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

  validator = defaults( jsonschema.Draft6Validator ) ; validator( schema ).validate( conf )
