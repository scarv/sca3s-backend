# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend as be
from sca3s import spec    as spec

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import docker, git, importlib, json, logging, more_itertools as mit, os, re, sys

class JobImp( be.share.job.JobAbs ) :
  def __init__( self, conf, path, log ) :
    super().__init__( conf, path, log )  

    self.version =      self.conf.get( 'version' )

    self.id      =      self.conf.get(      'id' )
    self.user_id = str( self.conf.get( 'user_id' ) )

  def _build_board( self ) :
    t = self.conf.get(  'board-id' )

    try :
      return importlib.import_module( 'sca3s.backend.acquire.board'  + '.' + t.replace( '/', '.' ) ).BoardImp( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % (  'board', t ) )
  
  def _build_scope( self ) :
    t = self.conf.get(  'scope-id' )
  
    try :
      return importlib.import_module( 'sca3s.backend.acquire.scope'  + '.' + t.replace( '/', '.' ) ).ScopeImp( self )  
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % (  'scope', t ) )
  
  def _build_driver( self ) :
    t = self.conf.get( 'driver-id' )
  
    try :
      return importlib.import_module( 'sca3s.backend.acquire.driver' + '.' + t.replace( '/', '.' ) ).DriverImp( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % ( 'driver', t ) )

  def _build_repo( self ) :
    t = self.conf.get(   'repo-id' )

    try :
      return importlib.import_module( 'sca3s.backend.acquire.repo'   + '.' + t.replace( '/', '.' ) ).RepoImp( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % (   'repo', t ) )

  def _build_depo( self ) :
    t = self.conf.get(   'depo-id' )

    try :
      return importlib.import_module( 'sca3s.backend.acquire.depo'   + '.' + t.replace( '/', '.' ) ).DepoImp( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % (   'depo', t ) )

  # Prepare the repo.:
  # 
  # 1. create and initialise git index for repo.
  # 2. check repo. vs. whitelist
  #    - fetch upstream repo.
  #    - perform diff between origin/master and upstream/master
  #    - for each filename that differs, check vs. pattern

  def _prepare_repo( self ) :
    return # TODO: reinstance this once upstream repo. is public, otherwise auth. fails

    template_url     = be.share.sys.conf.get( 'template', section = 'security' ).get( 'url'     )
    template_tag     = be.share.sys.conf.get( 'template', section = 'security' ).get( 'tag'     )
    template_pattern = be.share.sys.conf.get( 'template', section = 'security' ).get( 'pattern' )

    path             = os.path.join( self.path, 'target' )

    self.log.indent_inc( message = 'building repo.' )

    try :
      repo = git.Repo( path = path )
    except git.exc.InvalidGitRepositoryError :
      repo = git.Repo.init( path = path )

      repo.git.add( all = True )
      repo.git.commit( message = ' constructed repo. from non-repo. source', all = True )

    self.log.indent_dec()

    self.log.indent_inc( message = 'checking repo.' )

    repo.create_remote( 'upstream', template_url ).fetch() ; fail = False

    for filename in repo.git.diff( 'upstream' + '/' + template_tag, name_only = True ).split( '\n' ) :
      if ( not filename.strip() ) :
        continue

      if( None == re.match( template_pattern, filename ) ) :
        self.log.info( '| failed: ' + filename ) ; fail = True
      else :
        self.log.info( '| passed: ' + filename )

    self.log.indent_dec()

    if ( fail ) :
      raise Exception()

  # Prepare the board:
  # 
  # 1. define parameters
  #    - construct the image name
  #    - construct the volume and environment mappings
  #    - remap volume mappings to reflect configuration (e.g., for Docker-by-Docker)
  # 2. build
  #    - fetch dependencies
  #    - build dependencies
  #    - build
  # 3. report
  # 4. program
  # 5. clean

  def _prepare_board( self ) :
    img = 'scarv' + '/' + 'sca3s-harness' + '.' + self.conf.get( 'board-id' ).replace( '/', '-' ) + ':' + be.share.version.VERSION
    
    vol = { os.path.join( self.path, 'target' ) : { 'bind' : '/mnt/scarv/sca3s/harness', 'mode' : 'rw' } }
    
    env = { 'DOCKER_GID' : os.getgid(), 
            'DOCKER_UID' : os.getuid(), 'CONTEXT' : 'native', 'BOARD' : self.conf.get( 'board-id' ), 'TARGET' : mit.first( self.conf.get( 'driver-id' ).split( '/' ) ), 'CONF' : ' '.join( [ '-D' + str( k ) + '=' + '"' + str( v ) + '"' for ( k, v ) in self.repo.conf.items() ] ) }

    vol = { **vol, **self.board.get_build_context_vol() }
    env = { **env, **self.board.get_build_context_env() }

    self.log.info( 'docker image       = %s', img )
    self.log.info( 'docker volume      = %s', vol )
    self.log.info( 'docker environment = %s', env )

    def step( cmd, privileged = False ) :
      self.log.indent_inc( message = 'docker build context => %s' % ( cmd ) )
      self.drain( 'stdout', docker.from_env().containers.run( img, command = cmd, environment = env, volumes = vol, privileged = privileged, detach = False, auto_remove = True, stdout = True, stderr = True ) )
      self.log.indent_dec()

    step( 'deps-fetch-harness', privileged = False )
    step( 'deps-build-harness', privileged = False )
    
    step(      'build-harness', privileged = False )
    step(     'report-harness', privileged = False )

    self.board.program()
    self.board.prepare()

    step(      'clean-harness', privileged = False )

  # Prepare the scope:
  # 
  # 1. transfer board parameters
  # 2. calibrate

  def _prepare_scope( self ) :
    trace_spec            = self.conf.get( 'trace-spec' )

    trace_resolution_id   =      trace_spec.get( 'resolution-id'   )
    trace_resolution_spec = int( trace_spec.get( 'resolution-spec' ) )

    trace_period_id       =      trace_spec.get( 'period-id'       )
    trace_period_spec     = int( trace_spec.get( 'period-spec'     ) )

    trace_type            =      trace_spec.get( 'type'            )

    self.scope.channel_trigger_range     = self.board.get_channel_trigger_range()
    self.scope.channel_trigger_threshold = self.board.get_channel_trigger_threshold()
    self.scope.channel_acquire_range     = self.board.get_channel_acquire_range()
    self.scope.channel_acquire_threshold = self.board.get_channel_acquire_threshold()

    if   ( trace_resolution_id == 'bit'  ) :
      trace_resolution = trace_resolution_spec
    elif ( trace_resolution_id == 'min'  ) :
      trace_resolution = scope.RESOLUTION_MIN
    elif ( trace_resolution_id == 'max'  ) :
      trace_resolution = scope.RESOLUTION_MAX

    if   ( trace_period_id == 'auto'      ) :
      t = self.driver.calibrate( resolution = trace_resolution, dtype = trace_type)
    elif ( trace_period_id == 'interval'  ) :
      t = self.scope.calibrate( scope.CALIBRATE_MODE_INTERVAL,  trace_period_spec, resolution = trace_resolution, dtype = trace_type )
    elif ( trace_period_id == 'frequency' ) :
      t = self.scope.calibrate( scope.CALIBRATE_MODE_FREQUENCY, trace_period_spec, resolution = trace_resolution, dtype = trace_type )
    elif ( trace_period_id == 'duration'  ) :
      t = self.scope.calibrate( scope.CALIBRATE_MODE_DURATION,  trace_period_spec, resolution = trace_resolution, dtype = trace_type )

    self.log.info( 'conf = %s', t )

  # Execute job process prologue (i.e., *before* process):
  #
  # 1. dump configuration
  # 2. construct board, scope, driver, repo., and depo. objects
  # 3. open  board object
  # 4. open  scope object

  def process_prologue( self ) :
    self.log.indent_inc( message = 'dump configuration' )
    self.conf.dump( self.log, level = logging.INFO )
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

  # Execute job process:
  #
  # 1. transfer target implementation from repo. to local copy 
  # 2. prepare repo.,  e.g., check vs. diff
  # 3. prepare board,  e.g., build and program target implementation
  # 4. prepare driver, e.g., query target implemention parameters
  # 5. prepare scope,  e.g., calibrate wrt. target implementation
  # 6. execute driver, i.e., acquisition process wrt. target implementation
  # 7. transfer target implementation from local copy to depo.

  def process( self ) :
    self.log.indent_inc( message = 'transfer local <- repo.' )
    self.repo.transfer()
    self.log.indent_dec()

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

    self.log.indent_inc( message = 'transfer local -> depo.' )
    self.depo.transfer()
    self.log.indent_dec()

  # Execute job process epilogue (i.e., *after*  process):
  #
  # 1. close scope object
  # 2. close board object

  def process_epilogue( self ) :
    self.log.indent_inc( message = 'close scope' )
    self.scope.close()
    self.log.indent_dec()

    self.log.indent_inc( message = 'close board' )
    self.board.close()
    self.log.indent_dec()
