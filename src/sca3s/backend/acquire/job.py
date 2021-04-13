# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import hybrid as hybrid

from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import git, importlib, json, logging, os, re, sys

class JobImp( sca3s_be.share.job.JobAbs ) :
  def __init__( self, conf, path, log ) :
    super().__init__( conf, path, log )  

    self.user_id     = int( self.conf.get( 'user_id'      ) )

    self.job_id      =      self.conf.get(  'job_id'      )
    self.job_version =      self.conf.get(  'job_version' )

    self.board       = None
    self.scope       = None

    self.driver      = None

    self.repo        = None
    self.depo        = None

  # Construct a parameterised job-related object.

  def _object( self, id, module, cons ) :
    try :
      t = importlib.import_module( 'sca3s.backend.acquire.%s' % ( module )  + '.' + id.replace( '/', '.' ) ) ; t = getattr( t, cons ) ; return t( self )
    except :
      raise ImportError( 'failed to construct %s instance with id = %s ' % ( module, id ) )

  # Prepare the board:
  # 
  # 1. clean
  # 2. build
  #    - fetch dependencies
  #    - build dependencies
  #    - build
  # 3. report  
  #    - dump  target image structure via, e.g., readelf
  #    - dump  non-interactive I/O responses
  #    - parse non-interactive I/O responses
  # 4. program
  #    - hardware step
  #    - software step
  # 5. prepare

  def _prepare_board( self ) :
    self.exec_docker(  'clean-harness' )
    self.exec_docker(  'build-harness' )

    self.exec_docker( 'report-harness' )
    self.exec_docker(     'io-harness' )

    self.board.io()

    self.board.program_hw()
    self.board.program_sw()

    self.board.prepare()

  # Prepare the scope:
  # 
  # 1. transfer board parameters
  # 2. calibrate

  def _prepare_scope( self ) :
    trace_spec            = self.conf.get( 'trace_spec' )

    trace_resolution_id   =      trace_spec.get( 'resolution_id'   )
    trace_resolution_spec = int( trace_spec.get( 'resolution_spec' ) )

    trace_period_id       =      trace_spec.get( 'period_id'       )
    trace_period_spec     = int( trace_spec.get( 'period_spec'     ) )

    trace_type            =      trace_spec.get( 'type'            )

    if   ( trace_resolution_id == 'bit'  ) :
      trace_resolution = trace_resolution_spec
    elif ( trace_resolution_id == 'min'  ) :
      trace_resolution = scope.RESOLUTION_MIN
    elif ( trace_resolution_id == 'max'  ) :
      trace_resolution = scope.RESOLUTION_MAX

    if   ( trace_period_id == 'duration'  ) :
      t = self.scope.calibrate( mode = scope.CALIBRATE_MODE_DURATION,  value = trace_period_spec, resolution = trace_resolution, dtype = trace_type )
    elif ( trace_period_id == 'interval'  ) :
      t = self.scope.calibrate( mode = scope.CALIBRATE_MODE_INTERVAL,  value = trace_period_spec, resolution = trace_resolution, dtype = trace_type )
    elif ( trace_period_id == 'frequency' ) :
      t = self.scope.calibrate( mode = scope.CALIBRATE_MODE_FREQUENCY, value = trace_period_spec, resolution = trace_resolution, dtype = trace_type )
    elif ( trace_period_id == 'auto'      ) :
      t = self.scope.calibrate( mode = scope.CALIBRATE_MODE_AUTO,                                 resolution = trace_resolution, dtype = trace_type )

    self.log.info( 'conf = %s', t )

  # Prepare the repo.:
  # 
  # 1. create and initialise git index for repo.
  # 2. check repo. vs. whitelist
  #    - fetch upstream repo.
  #    - perform diff between origin/master and upstream/master
  #    - for each filename that differs, check vs. pattern

  def _prepare_repo( self ) :
    template_url     = sca3s_be.share.sys.conf.get( 'template', section = 'security' ).get( 'url'     )
    template_tag     = sca3s_be.share.sys.conf.get( 'template', section = 'security' ).get( 'tag'     )
    template_pattern = sca3s_be.share.sys.conf.get( 'template', section = 'security' ).get( 'pattern' )

    path             = os.path.join( self.path, 'target' )

    self.log.indent_inc( message = 'building repo.' )

    try :
      repo = git.Repo( path = path )
    except git.exc.InvalidGitRepositoryError :
      repo = git.Repo.init( path = path )

      repo.git.add( all = True )
      repo.git.commit( message = 'constructed repo. from non-repo. source', all = True )

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
      raise Exception( 'failed repo. preparation' )

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

    if ( self.conf.get( 'board_id' ) == self.conf.get( 'scope_id' ) ) :
      self.log.indent_inc( message = 'construct hybrid object' )

      self.hybrid = self._object( self.conf.get(  'board_id' ), 'hybrid', 'HybridImp' ) 

      self.board  = self.hybrid.get_board() 
      self.scope  = self.hybrid.get_scope()

      self.log.indent_dec()
    
    else :
      self.log.indent_inc( message = 'construct board  object' )
      self.board  = self._object( self.conf.get(  'board_id' ),  'board',  'BoardImp' )
      self.log.indent_dec()
  
      self.log.indent_inc( message = 'construct scope  object' )
      self.scope  = self._object( self.conf.get(  'scope_id' ),  'scope',  'ScopeImp' )
      self.log.indent_dec()

    if ( True ) :
      self.log.indent_inc( message = 'construct driver object' )
      self.driver = self._object( self.conf.get( 'driver_id' ), 'driver', 'DriverImp' )
      self.log.indent_dec()

      self.log.indent_inc( message = 'construct repo   object' )
      self.repo   = self._object( self.conf.get(   'repo_id' ),   'repo',   'RepoImp' )
      self.log.indent_dec()

      self.log.indent_inc( message = 'construct depo   object' )
      self.depo   = self._object( self.conf.get(   'depo_id' ),   'depo',   'DepoImp' )
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

    self.log.indent_inc( message = 'process driver' )
    self.driver.process()
    self.log.indent_dec()

    self.log.indent_inc( message = 'transfer local -> depo.' )
    self.depo.transfer()
    self.log.indent_dec()

  # Execute job process epilogue (i.e., *after*  process):
  #
  # 1. close scope object
  # 2. close board object

  def process_epilogue( self ) :
    self.log.indent_rst()

    if( self.scope != None ) :
      self.log.indent_inc( message = 'close scope' )
      self.scope.close()
      self.log.indent_dec()

    if( self.board != None ) :
      self.log.indent_inc( message = 'close board' )
      self.board.close()
      self.log.indent_dec()
