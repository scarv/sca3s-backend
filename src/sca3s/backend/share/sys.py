# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import argparse, logging, os, sys, tempfile

CONF = {
  'type' : 'object', 'default' : {}, 'properties' : {
    'path:job'          : { 'type' :  'string',         'default' : tempfile.tempdir },
    'path:log'          : { 'type' :  'string',         'default' : tempfile.tempdir },

    'security:creds'    : { 'type' :  'object',         'default' : {}               },

    'security:template' : { 'type' :  'object',         'default' : {}, 'patternProperties' : {
          'url' : { 'type' :  'string', 'default' : 'git@github.com/scarv/sca3s-harness.git' },
          'tag' : { 'type' :  'string', 'default' : 'master'                                 },
      'pattern' : { 'type' :  'string', 'default' : 'README.md|sca3s.json|src/kernel/.*'     }
    } },

    'api:instance'        : { 'enum' : [ '1', '2', '*' ], 'default' :                       '*' },
    'api:url'             : { 'type' :  'string',         'default' : 'https://sca3s.scarv.org' },

    'api:retry_wait'      : { 'type' :  'number',         'default' :                         3 },
    'api:retry_count'     : { 'type' :  'number',         'default' :                         3 },

    'api:announce_wait'   : { 'type' :  'number',         'default' :                       600 },
    'api:announce_ping'   : { 'type' :  'number',         'default' :                         1 },
    'api:retrieve_wait'   : { 'type' :  'number',         'default' :                        30 },
    'api:retrieve_ping'   : { 'type' :  'number',         'default' :                        10 },

    'exec_native:env'     : { 'type' :  'object',         'default' :                        {} },
    'exec_native:timeout' : { 'type' :  'number',         'default' :                        60 },

    'exec_docker:env'     : { 'type' :  'object',         'default' :                        {} },
    'exec_docker:vol'     : { 'type' :  'object',         'default' :                        {} },
    'exec_docker:timeout' : { 'type' :  'number',         'default' :                         0 },
  
    'job:manifest_file'   : { 'type' :  'string'                                                },
    'job:manifest_data'   : { 'type' :  'string'                                                },
 
    'job:clean'           : { 'type' : 'boolean',         'default' :                     False },

    'job:device_db'       : { 'type' :  'object',         'default' : {}, 'patternProperties' : {
      '^.*$' : { 'type' : 'object', 'default' : {},
        'allOf' : [ {
          'oneOf' : [ { # options: board
            'properties' : { # giles
               'board_id'   : { 'type' : 'string', 'enum' : [ 'giles' ]                          },
               'board_desc' : { 'type' : 'string'                                                },
               'board_mode' : { 'type' : 'string', 'enum' : [                'non-interactive' ] },
               'board_spec' : { 'type' : 'object', 'default' : {}, 'properties' : {

               }, 'required' : [] },
               'board_path' : { 'type' :  'array', 'default' : [], 'items' : { 
                 'type' : 'string' 
               } }
            }
          }, {
            'properties' : { # scale/lpc1313fbd48
               'board_id'   : { 'type' : 'string', 'enum' : [ 'scale/lpc1313fbd48' ]             },
               'board_desc' : { 'type' : 'string'                                                },
               'board_mode' : { 'type' : 'string', 'enum' : [ 'interactive', 'non-interactive' ] },
               'board_spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
                         'connect_id'      : { 'type' : 'string'                                                },
                         'connect_timeout' : { 'type' : 'number'                                                },
        
                         'program_id'      : { 'type' : 'string'                                                },
                         'program_timeout' : { 'type' : 'number'                                                },
                         'program_mode'    : { 'type' : 'string', 'enum' : [ 'jlink', 'usb' ]                   }
               }, 'required' : [ 'connect_id', 'connect_timeout', 'program_id', 'program_timeout', 'program_mode' ] },
               'board_path' : { 'type' :  'array', 'default' : [], 'items' : { 
                 'type' : 'string' 
               } }
            }
          }, {
            'properties' : { # cw308/stm32f071rbt6
               'board_id'   : { 'type' : 'string', 'enum' : [ 'cw308/stm32f071rbt6' ]            },
               'board_desc' : { 'type' : 'string'                                                },
               'board_mode' : { 'type' : 'string', 'enum' : [ 'interactive', 'non-interactive' ] },
               'board_spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
                         'connect_id'      : { 'type' : 'string'                                                },
                         'connect_timeout' : { 'type' : 'number'                                                },
        
                         'program_id'      : { 'type' : 'string'                                                },
                         'program_timeout' : { 'type' : 'number'                                                },
                         'program_mode'    : { 'type' : 'string', 'enum' : [ 'jlink' ]                          }
               }, 'required' : [ 'connect_id', 'connect_timeout', 'program_id', 'program_timeout', 'program_mode' ] },
               'board_path' : { 'type' :  'array', 'default' : [], 'items' : { 
                 'type' : 'string' 
               } }
            }
          }, {
            'properties' : { # cw308/stm32f405rgt6
               'board_id'   : { 'type' : 'string', 'enum' : [ 'cw308/stm32f405rgt6' ]            },
               'board_desc' : { 'type' : 'string'                                                },
               'board_mode' : { 'type' : 'string', 'enum' : [ 'interactive', 'non-interactive' ] },
               'board_spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
                         'connect_id'      : { 'type' : 'string'                                                },
                         'connect_timeout' : { 'type' : 'number'                                                },
        
                         'program_id'      : { 'type' : 'string'                                                },
                         'program_timeout' : { 'type' : 'number'                                                },
                         'program_mode'    : { 'type' : 'string', 'enum' : [ 'jlink' ]                          }
               }, 'required' : [ 'connect_id', 'connect_timeout', 'program_id', 'program_timeout', 'program_mode' ] },
               'board_path' : { 'type' :  'array', 'default' : [], 'items' : { 
                 'type' : 'string' 
               } }
            }
          } ] }, {
          'oneOf' : [ { # options: scope
            'properties' : { # picoscope/ps2206b
               'scope_id'   : { 'enum' : [ 'picoscope/ps2206b' ]                                 },
               'scope_desc' : { 'type' : 'string'                                                },
               'scope_mode' : { 'type' : 'string', 'enum' : [ 'interactive'                    ] },
               'scope_spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
                         'connect_id'      : { 'type' : 'string' },
                         'connect_timeout' : { 'type' : 'number' },
      
                         'acquire_timeout' : { 'type' : 'number' },

                 'channel_trigger_id'      : { 
                   'type' : 'string', 'enum' : [ 'A', 'B' ] 
                  },
                 'channel_acquire_id'      : {
                   'type' : 'string', 'enum' : [ 'A', 'B' ]
                  },
                 'channel_disable_id'      : { 'type' :  'array', 'default' : [], 'items' : {
                   'type' : 'string', 'enum' : [ 'A', 'B' ]
                 } },
               }, 'required' : [ 'connect_id', 'connect_timeout', 'channel_trigger_id', 'channel_acquire_id' ] },
               'scope_path' : { 'type' :  'array', 'default' : [], 'items' : { 
                 'type' : 'string' 
               } }
            }
          }, {
            'properties' : { # picoscope/ps3406b
               'scope_id'   : { 'enum' : [ 'picoscope/ps3406b' ]                                 },
               'scope_desc' : { 'type' : 'string'                                                },
               'scope_mode' : { 'type' : 'string', 'enum' : [ 'interactive'                    ] },
               'scope_spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
                         'connect_id'      : { 'type' : 'string' },
                         'connect_timeout' : { 'type' : 'number' },

                         'acquire_timeout' : { 'type' : 'number' },
        
                 'channel_trigger_id'      : { 
                   'type' : 'string', 'enum' : [ 'A', 'B', 'C', 'D' ] 
                  },
                 'channel_acquire_id'      : {
                   'type' : 'string', 'enum' : [ 'A', 'B', 'C', 'D' ]
                  },
                 'channel_disable_id'      : { 'type' :  'array', 'default' : [], 'items' : {
                   'type' : 'string', 'enum' : [ 'A', 'B', 'C', 'D' ]
                 } }
               }, 'required' : [ 'connect_id', 'connect_timeout', 'channel_trigger_id', 'channel_acquire_id' ] },
               'scope_path' : { 'type' :  'array', 'default' : [], 'items' : { 
                 'type' : 'string' 
               } }
            }
          }, {
            'properties' : { # giles
               'scope_id'   : { 'enum' : [ 'giles' ]                                             },
               'scope_desc' : { 'type' : 'string'                                                },
               'scope_mode' : { 'type' : 'string', 'enum' : [                'non-interactive' ] },
               'scope_spec' : { 'type' : 'object', 'default' : {}, 'properties' : {
                         'acquire_timeout' : { 'type' : 'number' }
               }, 'required' : [] },
               'scope_path' : { 'type' :  'array', 'default' : [], 'items' : { 
                 'type' : 'string' 
               } }
            }
          } ] } ],
        'required' : [ 'board_id', 'board_desc', 'board_spec', 'scope_id', 'scope_desc', 'scope_spec' ]
      } }
    }
  }
}

conf = None
log  = None

def init() :
  global conf, log

  # parse command line arguments

  parser = argparse.ArgumentParser( add_help = False )
  
  parser.add_argument( '--sys:help',          action =    'help'                                                                               )
  parser.add_argument( '--sys:version',       action = 'version',                                     version = sca3s_be.share.version.VERSION )
  parser.add_argument( '--sys:debug',         action =   'count',                                     default = 0                              )

  parser.add_argument( '--sys:conf',          action =   'store', type = str                                                                   )

  parser.add_argument( '--sys:task',          action =   'store', choices = [ 'acquire', 'analyse' ], default = 'acquire'                      )
  parser.add_argument( '--sys:mode',          action =   'store', choices = [ 'cli', 'api'         ], default = 'cli'                          )

  parser.add_argument( '--job:manifest_file', action =   'store', type = str                                                                   )
  parser.add_argument( '--job:manifest_json', action =   'store', type = str                                                                   )

  args = { k : v for ( k, v ) in vars( parser.parse_args() ).items() if ( v != None ) }

  # initialise system configuration, from configuration file *then* command line arguments

  conf = sca3s_be.share.conf.Conf()

  if ( ( 'sys:conf' in args ) and ( os.path.isfile( args[ 'sys:conf' ] ) ) ) :
    conf.populate( args[ 'sys:conf' ] )

  conf.populate( args )

  sca3s_mw.share.schema.validate( conf, CONF )

  # initialise system logger

  log  = sca3s_be.share.log.build_log( sca3s_be.share.log.TYPE_SYS, path = sca3s_be.share.sys.conf.get( 'log', section = 'path' ) )

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
