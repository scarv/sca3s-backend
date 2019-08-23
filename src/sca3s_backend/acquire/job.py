# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

import sca3s_backend as be
import sca3s_spec    as spec

from sca3s_backend.acquire import board  as board
from sca3s_backend.acquire import scope  as scope
from sca3s_backend.acquire import driver as driver

from sca3s_backend.acquire import repo   as repo
from sca3s_backend.acquire import depo   as depo

import git, importlib, json, more_itertools as mit, os, re, sys

class JobImp( be.share.job.JobAbs ) :
  def __init__( self, conf, path, log ) :
    super().__init__( conf, path, log )  

    self.version =      self.conf.get( 'version' )
    self.id      =      self.conf.get(      'id' )
    self.user_id = str( self.conf.get( 'user_id' ) )

  def _build_board( self ) :
    t = self.conf.get(  'board-id' )

    try :
      return importlib.import_module( 'sca3s_backend.acquire.board'  + '.' + t.replace( '/', '.' ) ).BoardImp( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % (  'board', t ) )
  
  def _build_scope( self ) :
    t = self.conf.get(  'scope-id' )
  
    try :
      return importlib.import_module( 'sca3s_backend.acquire.scope'  + '.' + t.replace( '/', '.' ) ).ScopeImp( self )  
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % (  'scope', t ) )
  
  def _build_driver( self ) :
    t = self.conf.get( 'driver-id' )
  
    try :
      return importlib.import_module( 'sca3s_backend.acquire.driver' + '.' + t.replace( '/', '.' ) ).DriverImp( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % ( 'driver', t ) )

  def _build_repo( self ) :
    t = self.conf.get(   'repo-id' )

    try :
      return importlib.import_module( 'sca3s_backend.acquire.repo'   + '.' + t.replace( '/', '.' ) ).RepoImp( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % (   'repo', t ) )

  def _build_depo( self ) :
    t = self.conf.get(   'depo-id' )

    try :
      return importlib.import_module( 'sca3s_backend.acquire.depo'   + '.' + t.replace( '/', '.' ) ).DepoImp( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % (   'depo', t ) )

  # 1. create and initialise git index for repo.
  # 2. check repo. vs. whitelist
  #    - fetch upstream repo.
  #    - perform diff between origin/master and upstream/master
  #    - for each filename that differs, check vs. pattern

  def _prepare_repo( self ) :
    return # TODO: reinstance this once upstream repo. is public, otherwise auth. fails

    diff_url     = be.share.sys.conf.get( 'diff-url',     section = 'security' )
    diff_pattern = be.share.sys.conf.get( 'diff-pattern', section = 'security' )

    path              = os.path.join( self.path, 'target' )

    self.log.indent_inc( message = 'building repo.' )

    try :
      repo = git.Repo( path = path )
    except git.exc.InvalidGitRepositoryError :
      repo = git.Repo.init( path = path )

      repo.git.add( all = True )
      repo.git.commit( message = ' constructed repo. from non-repo. source', all = True )

    self.log.indent_dec()

    self.log.indent_inc( message = 'checking repo.' )

    repo.create_remote( 'upstream', diff_url ).fetch() ; fail = False

    for filename in repo.git.diff( 'upstream/master', name_only = True ).split( '\n' ) :
      if ( not filename.strip() ) :
        continue

      if( None == re.match( diff_pattern, filename ) ) :
        self.log.info( '| failed: ' + filename ) ; fail = True
      else :
        self.log.info( '| passed: ' + filename )

    self.log.indent_dec()

    if ( fail ) :
      raise Exception()

  # 1. build
  #    - fetch dependencies
  #    - build dependencies
  #    - build
  # 2. program
  # 3. clean

  def _prepare_board( self ) :
    #def f( stdout, stderr ) :
    #  self._drain( 'stdout', stdout )
    #  self._drain( 'stderr', stderr )
    #
    #client = docker.from_env()
    #
    #vol = { os.path.abspath( './data/git' ) : { 'bind' : '/acquire/git', 'mode' : 'rw' },
    #        os.path.abspath( './data/job' ) : { 'bind' : '/acquire/job', 'mode' : 'rw' } }
    #
    #env = { 'DOCKER_GID' : os.getgid(), 
    #        'DOCKER_UID' : os.getuid(), 
    #                
    #        'REPO_HOME' : '/acquire/job/target', 'BOARD' : self.conf.get( 'board-id' ), 'TARGET' : mit.first( self.conf.get( 'driver-id' ).split( '/' ) ), 'CONF' : ' '.join( [ '-D' + str( k ) + '=' + '"' + str( v ) + '"' for ( k, v ) in self.repo.conf.items() ] ), 'CACHE' : '/acquire/git' }
    #
    #container = client.containers.run( 'scarv/lab-target' + be.share.version.VERSION, 'bash', environment = env, volumes = vol, name = 'acquire', detach = True, tty = True )
    #
    #f( container.exec_run( "gosu %d:%d bash -c 'make -C ${REPO_HOME} deps-fetch'" % ( os.getuid(), os.getgid() ), environment = env, demux = True ) )
    #f( container.exec_run( "gosu %d:%d bash -c 'make -C ${REPO_HOME} deps-build'" % ( os.getuid(), os.getgid() ), environment = env, demux = True ) )
    #
    #f( container.exec_run( "gosu %d:%d bash -c 'make -C ${REPO_HOME}      build'" % ( os.getuid(), os.getgid() ), environment = env, demux = True ) )
    #self.board.program()
    #f( container.exec_run( "gosu %d:%d bash -c 'make -C ${REPO_HOME}      clean'" % ( os.getuid(), os.getgid() ), environment = env, demux = True ) )
    #
    #container.stop() ; container.remove( force = True )

    env = { 'REPO_HOME' : os.path.join( self.path, 'target' ), 'BOARD' : self.conf.get( 'board-id' ), 'TARGET' : mit.first( self.conf.get( 'driver-id' ).split( '/' ) ), 'CONF' : ' '.join( [ '-D' + str( k ) + '=' + '"' + str( v ) + '"' for ( k, v ) in self.repo.conf.items() ] ), 'CACHE' : be.share.sys.conf.get( 'git', section = 'path' ) }

    self.run( [ 'make', '-C', 'target', '--no-builtin-rules', 'deps-fetch' ], env = env )
    self.run( [ 'make', '-C', 'target', '--no-builtin-rules', 'deps-build' ], env = env )
    self.run( [ 'make', '-C', 'target', '--no-builtin-rules',      'build' ], env = env )

    self.board.program()

    self.run( [ 'make', '-C', 'target', '--no-builtin-rules',      'clean' ], env = env )

  def _prepare_scope( self ) :
    trace_spec            = self.conf.get( 'trace-spec' )

    trace_period_id       = trace_spec.get( 'period-id'       )
    trace_period_spec     = trace_spec.get( 'period-spec'     )

    trace_resolution_id   = trace_spec.get( 'resolution-id'   )
    trace_resolution_spec = trace_spec.get( 'resolution-spec' )

    self.scope.channel_trigger_range     = self.board.get_channel_trigger_range()
    self.scope.channel_trigger_threshold = self.board.get_channel_trigger_threshold()
    self.scope.channel_acquire_range     = self.board.get_channel_acquire_range()
    self.scope.channel_acquire_threshold = self.board.get_channel_acquire_threshold()

    if ( trace_period_id == 'auto' ) :
      l = be.share.sys.conf.get( 'timeout', section = 'job' )
    
      t = self.scope.conf( scope.CONF_MODE_DURATION, 1 * l )

      self.log.info( 'before calibration, configuration = %s', t )

      trace = self.driver.acquire() ; l = be.share.util.measure( be.share.util.MEASURE_MODE_DURATION, trace[ 'trigger' ], self.scope.channel_trigger_threshold ) * self.scope.signal_interval
      t = self.scope.conf( scope.CONF_MODE_DURATION, 2 * l )

      trace = self.driver.acquire() ; l = be.share.util.measure( be.share.util.MEASURE_MODE_DURATION, trace[ 'trigger' ], self.scope.channel_trigger_threshold ) * self.scope.signal_interval
      t = self.scope.conf( scope.CONF_MODE_DURATION, 1 * l )

      self.log.info( 'after  calibration, configuration = %s', t )

    else :
      l = trace_period_spec

      if   ( trace_period_id == 'interval'  ) :
        t = self.scope.conf( scope.CONF_MODE_INTERVAL,  l )
      elif ( trace_period_id == 'frequency' ) :
        t = self.scope.conf( scope.CONF_MODE_FREQUENCY, l )
      elif ( trace_period_id == 'duration'  ) :
        t = self.scope.conf( scope.CONF_MODE_DURATION,  l )

      self.log.info(                     'configuration = %s', t )

  # Execute job process prologue (i.e., *before* process):
  #
  # 1. dump configuration
  # 2. construct board, scope, driver, repo., and depo. objects
  # 3. open  board object
  # 4. open  scope object
  # 5. transfer target implementation from repo. to local copy 

  def process_prologue( self ) :
    self.log.indent_inc( message = 'dump configuration' )

    n = 0

    for ( key, value ) in sorted( self.conf.items() ) : 
      n = max( n, len( key ) )

    for ( key, value ) in sorted( self.conf.items() ) :
      self.log.info( '{0:<{width}} = {1}'.format( key, json.dumps( value ), width = n ) )

    self.log.indent_dec()

    self.log.indent_inc( message = 'construct board  object' )
    self.board = self._build_board()
    self.log.indent_dec()

    self.log.indent_inc( message = 'construct scope  object' )
    self.scope = self._build_scope()
    self.log.indent_dec()

    self.log.indent_inc( message = 'construct driver object' )
    self.driver= self._build_driver()
    self.log.indent_dec()

    self.log.indent_inc( message = 'construct repo   object' )
    self.repo  = self._build_repo()
    self.log.indent_dec()

    self.log.indent_inc( message = 'construct depo   object' )
    self.depo  = self._build_depo()
    self.log.indent_dec()

    self.log.indent_inc( message = 'open  board' )
    self.board.open()
    self.log.indent_dec()

    self.log.indent_inc( message = 'open  scope' )
    self.scope.open()
    self.log.indent_dec()

    self.log.indent_inc( message = 'transfer local <- repo.' )
    self.repo.transfer()
    self.log.indent_dec()

  # Execute job process:
  #
  # 1. prepare repo.,  e.g., check vs. diff
  # 1. prepare board,  e.g., build and program target implementation
  # 2. prepare driver, e.g., query target implemention parameters
  # 3. prepare scope,  e.g., calibrate wrt. target implementation
  # 4. execute driver, i.e., acquisition process wrt. target implementation

  def process( self ) :
    self.log.indent_inc( message = 'prepare repo.'  )
    self._prepare_repo()
    self.log.indent_dec()

    self.log.indent_inc( message = 'prepare board'  )
    self._prepare_board()
    self.log.indent_dec()

    self.log.indent_inc( message = 'prepare driver' )
    self.driver.prepare()
    self.log.indent_dec()

    self.log.indent_inc( message = 'prepare scope'  )
    self._prepare_scope()
    self.log.indent_dec()

    self.log.indent_inc( message = 'execute driver' )
    self.driver.execute()
    self.log.indent_dec()

  # Execute job process epilogue (i.e., *after*  process):
  #
  # 1. transfer target implementation from local copy to depo.
  # 2. close scope object
  # 3. close board object

  def process_epilogue( self ) :
    self.log.indent_inc( message = 'transfer local -> depo.' )
    self.depo.transfer()
    self.log.indent_dec()

    self.log.indent_inc( message = 'close scope' )
    self.scope.close()
    self.log.indent_dec()

    self.log.indent_inc( message = 'close board' )
    self.board.close()
    self.log.indent_dec()
