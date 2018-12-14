# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share

import importlib, json, os, subprocess, sys, tempfile

class Job( object ) :
  def __init__( self, conf ) :
    super().__init__()  

    self.conf    = conf

    schema = { 
      'type' : 'object', 'default' : {}, 'properties' : {
        'version'               : { 'type' : 'string' },
        'id'                    : { 'type' : 'string' },
      
        'repo-id'               : { 'type' : 'string' },
        'repo-spec'             : { 'type' : 'object' },
        'depo-id'               : { 'type' : 'string' },
        'depo-spec'             : { 'type' : 'object' },

        'driver-id'             : { 'type' : 'string' },
        'driver-spec'           : { 'type' : 'object' },

        'device-id'             : { 'type' : 'string' },
      
        'trace-count'           : { 'type' : 'number', 'default' : 1 },
        'trace-format'          : { 'type' : 'string', 'default' : 'pickle', 'enum' : [ 'pickle', 'trs'                             ] },

        'trace-period-id'       : { 'type' : 'string', 'default' :   'auto', 'enum' : [ 'auto', 'interval', 'frequency', 'duration' ] },
        'trace-period-spec'     : { 'type' : 'number' },
        'trace-resolution-id'   : { 'type' : 'string', 'default' :   'auto', 'enum' : [ 'auto', 'bit'                               ] },
        'trace-resolution-spec' : { 'type' : 'number' }
      }
    }

    share.conf.validate( self.conf, schema )

    self.version = self.conf.get( 'version' )
    self.id      = self.conf.get(      'id' )

    if ( self.version != share.version.VERSION ) :
      raise share.exception.ConfigurationException()

    db = share.sys.conf.get( 'device-db', section = 'job' )

    if ( db.has( self.conf.get( 'device-id' ) ) ) :
      for ( key, value ) in db.get( self.conf.get( 'device-id' ) ).items() :
        self.conf.put( key, value )
    else :
      raise share.exception.ConfigurationException()

  def _build_device_board( self ) :
    t = self.conf.get(  'board-id' )

    try :
      return importlib.import_module( 'acquire.device.board' + '.' + t.replace( '/', '.' ) ).BoardImp( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % (  'board', t ) )
  
  def _build_device_scope( self ) :
    t = self.conf.get(  'scope-id' )
  
    try :
      return importlib.import_module( 'acquire.device.scope' + '.' + t.replace( '/', '.' ) ).ScopeImp( self )  
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % (  'scope', t ) )
  
  def _build_driver( self ) :
    t = self.conf.get( 'driver-id' )
  
    try :
      return importlib.import_module( 'acquire.driver'       + '.' + t.replace( '/', '.' ) ).DriverImp( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % ( 'driver', t ) )

  def _build_repo( self ) :
    t = self.conf.get(   'repo-id' )

    try :
      return importlib.import_module( 'acquire.repo'         + '.' + t.replace( '/', '.' ) ).RepoImp( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % (   'repo', t ) )

  def _build_depo( self ) :
    t = self.conf.get(   'depo-id' )

    try :
      return importlib.import_module( 'acquire.depo'         + '.' + t.replace( '/', '.' ) ).DepoImp( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % (   'depo', t ) )

  def extern( self, x, env = None, quiet = False, fail = True ) :
    if ( env == None ) :
      env = dict()

    env.update( os.environ )

    if ( not quiet ) :
      self.log.indent_inc( message = 'execute' )

    if ( not quiet ) :
      self.log.info( '| command : %s', ' '.join( x ) )

    try :
      pd = subprocess.run( x, cwd = self.path, env = env, timeout = int( share.sys.conf.get( 'extern', section = 'timeout' ) ), stdout = subprocess.PIPE, stderr = subprocess.PIPE )

      if ( not quiet ) :
        stdout = pd.stdout.decode().split( '\n' )
        stderr = pd.stderr.decode().split( '\n' )
      
        if ( ( len( stdout ) > 0 ) and ( stdout[ -1 ] == '' ) ) :
          stdout.pop()
        if ( ( len( stderr ) > 0 ) and ( stderr[ -1 ] == '' ) ) :
          stderr.pop()
      
        for t in stdout :
          self.log.info( '< stdout  : %s', t )
        for t in stderr :
          self.log.info( '< stderr  : %s', t )

      result = pd.returncode ; result_str = 'success' if ( result == 0 ) else 'failure'

    except subprocess.TimeoutExpired :
      result = -1            ; result_str = 'timeout'

    if ( not quiet ) :    
      self.log.info( '| result  : %s (exit status = %d)', result_str, result )

    if ( not quiet ) :
      self.log.indent_dec()

    if ( ( fail == True ) and ( result != 0 ) ) :
      raise ExecuteException()

    return ( result == 0 )

  def process_prologue( self ) :
    self.path = tempfile.mkdtemp( prefix = self.id + '.', dir = share.sys.conf.get( 'job', section = 'path' ) ) ; os.chdir( self.path )

    self.log = share.log.build_log_job( name = self.id )

    self.log.indent_inc( message = 'configuration' )

    n = 0

    for ( key, value ) in sorted( self.conf.items() ) : 
      if ( key.startswith( 'job' ) ) :
        n = max( n, len( key ) )

    for ( key, value ) in sorted( self.conf.items() ) :
      if ( key.startswith( 'job' ) ) :
        self.log.info( '{0:<{width}} = {1}'.format( key, json.dumps( value ), width = n ) )

    self.log.indent_dec()

    self.log.indent_inc( message = 'construct board  object' )
    self.device_board = self._build_device_board()
    self.log.indent_dec()

    self.log.indent_inc( message = 'construct scope  object' )
    self.device_scope = self._build_device_scope()
    self.log.indent_dec()

    self.log.indent_inc( message = 'construct driver object' )
    self.driver       = self._build_driver()
    self.log.indent_dec()

    self.log.indent_inc( message = 'construct repo   object' )
    self.repo         = self._build_repo()
    self.log.indent_dec()

    self.log.indent_inc( message = 'construct depo   object' )
    self.depo         = self._build_depo()
    self.log.indent_dec()

    self.log.indent_inc( message = 'transfer local <- repo.' )
    self.repo.transfer()
    self.log.indent_dec()

  def process( self ) :
    self.log.indent_inc( message = 'run driver -> process_prologue' )
    self.driver.process_prologue()
    self.log.indent_dec()

    self.log.indent_inc( message = 'run driver -> process'          )
    self.driver.process()
    self.log.indent_dec()

    self.log.indent_inc( message = 'run driver -> process_epilogue' )
    self.driver.process_epilogue()
    self.log.indent_dec()

  def process_epilogue( self ) :
    self.log.indent_inc( message = 'transfer local -> depo.' )
    self.depo.transfer()
    self.log.indent_dec()
