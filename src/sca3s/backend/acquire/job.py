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

from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import git, importlib, json, logging, os, re, sys

class JobImp( sca3s_be.share.job.JobAbs ) :
  def __init__( self, conf, path ) :
    super().__init__( conf, path )  

    self.board       = None
    self.scope       = None

    self.driver      = None

    self.repo        = None
    self.depo        = None

  # Construct a parameterised job-related object.

  def _object( self, x, m, f ) :
    x = x.replace( '/', '.' )
    m = m.replace( '/', '.' )

    x = 'sca3s.backend.acquire.{1:s}.{0:s}'.format( x, m )

    try :
      f = getattr( importlib.import_module( x ), f ) ; return f( self )
    except :
      raise ImportError( 'failed to construct %s instance' % ( x ) )

  # Prepare the board.
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
    self.log.indent_inc( message = 'build   harness' )

    self.exec_docker(  'clean-harness' )
    self.exec_docker(  'build-harness' )

    self.exec_docker( 'report-harness' )
    self.exec_docker(     'io-harness' )

    self.board.io()

    self.log.indent_dec()

    self.log.indent_inc( message = 'program board (hardware step)' )
    self.board.program_hw()
    self.log.indent_dec()

    self.log.indent_inc( message = 'program board (software step)' )
    self.board.program_sw()
    self.log.indent_dec()

    self.log.indent_inc( message = 'prepare harness' )
    self.board.prepare()
    self.log.indent_dec()

  # Prepare the scope.
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

  # Prepare the repo.
  # 
  # 1. create and initialise git index for repo.
  # 2. check repo. vs. whitelist
  #    - fetch upstream repo.
  #    - perform diff between origin/master and upstream/master
  #    - for each filename that differs, check vs. pattern

  def _prepare_repo( self ) :
    template_enforce = sca3s_be.share.sys.conf.get( 'template', section = 'security' ).get( 'enforce' )

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

    commit_lhs = repo.commit( 'upstream' + '/' + template_tag )
    commit_rhs = repo.commit()

    for entry in commit_lhs.diff( commit_rhs ) :
      if   ( ( entry.a_blob == None ) and ( entry.b_blob != None ) ) : # file   added
        filename = str( entry.b_path ).strip()

        if( True ) :
          self.log.info( '|   added -> passed: ' + filename )

      elif ( ( entry.a_blob != None ) and ( entry.b_blob == None ) ) : # file deleted
        filename = str( entry.a_path ).strip()

        if( True ) :
          self.log.info( '| deleted -> failed: ' + filename ) ; fail = True

      elif ( ( entry.a_blob != None ) and ( entry.b_blob != None ) ) : # file changed
        filename = str( entry.a_path ).strip()

        if( None == re.match( template_pattern, filename ) ) :
          self.log.info( '| changed -> failed: ' + filename ) ; fail = True
        else :
          self.log.info( '| changed -> passed: ' + filename )

    self.log.indent_dec()

    if ( template_enforce and fail ) :
      raise Exception( 'failed repo. preparation' )

  # Prepare the depo.

  def _prepare_depo( self ) :
    pass

  # Execute job prologue.

  def execute_prologue( self ) :
    self.log.banner()
  
    self.log.indent_inc( message = 'dump manifest' )
    self.conf.dump( self.log, level = logging.INFO )
    self.log.indent_dec()

  # Execute job.
  #
  # 1. - construct board
  #    - construct scope
  #    - construct repo.
  #    - construct depo.
  #
  # 2. - open      board
  #    - prepare   board,          e.g., build and program target implementation
  #
  # 3. - transfer  target implementation from repo. to local copy 
  #
  # 4. - prepare   repo.,          e.g., check changes vs. those allowed
  #    - prepare   depo.
  #
  # 5. - construct driver
  #    - prepare   driver,         e.g., query target implemention parameters
  #
  # 6. - open      scope
  #    - prepare   scope,          e.g., calibrate wrt. target implementation
  #
  # 7. - execute  driver prologue, e.g., job-specific  pre-processing/computation
  #    - execute  driver,          i.e., acquisition process wrt. target implementation
  #    - execute  driver epilogue, e.g., job-specific post-processing/computation
  #
  # 8. - transfer target implementation from local copy to depo.
  #
  # 9. - close     board
  #    - close     scope

  def execute( self ) :
    try :
      self.log.indent_rst()

      self.result_transfer[ 'acquire.log'     ] = { 'ContentType':        'text/plain',        'CacheControl': 'no-cache, max-age=0' }
      self.result_transfer[ 'acquire.hdf5.gz' ] = { 'ContentType': 'application/octet-stream', 'CacheControl': 'no-cache, max-age=0' }

      if ( self.conf.get( 'board_id' ) == self.conf.get( 'scope_id' ) ) :
        self.log.indent_inc( message = 'construct hybrid object' )
        self.hybrid = self._object( self.conf.get(  'board_id' ), 'hybrid', 'HybridImp' ) 
        self.log.indent_dec()
  
        self.log.indent_inc( message = 'construct board  object' )
        self.board  = self.hybrid.get_board() 
        self.log.indent_dec()
    
        self.log.indent_inc( message = 'construct scope  object' )
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
        self.log.indent_inc( message = 'construct repo   object' )
        self.repo   = self._object( self.conf.get(   'repo_id' ),   'repo',   'RepoImp' )
        self.log.indent_dec()
  
        self.log.indent_inc( message = 'construct depo   object' )
        self.depo   = self._object( self.conf.get(   'depo_id' ),   'depo',   'DepoImp' )
        self.log.indent_dec()

        self.log.indent_inc( message = 'transfer local <- repo.' )
        self.repo.transfer()
        self.log.indent_dec()
    
        self.log.indent_inc( message = 'prepare repo.'           )
        self._prepare_repo()
        self.log.indent_dec()

        self.log.indent_inc( message = 'prepare depo.'           )
        self._prepare_depo()
        self.log.indent_dec()

        self.log.indent_inc( message = 'open board'              )
        self.board.open()
        self.log.indent_dec()
  
        self.log.indent_inc( message = 'prepare board'           )
        self._prepare_board()
        self.log.indent_dec()

        if ( not sca3s_be.share.version.match( self.board.kernel_version ) ) :
          raise Exception( 'inconsistent kernel version'    )
        if ( self.conf.get( 'driver_id' ) != ( self.board.kernel_id      ) ) :
          raise Exception( 'inconsistent kernel identifier' )

        self.log.indent_inc( message = 'construct driver object' )
        self.driver = self._object( self.board.kernel_id + '/' + self.board.kernel_id_nameof, 'driver', 'DriverImp' )
        self.log.indent_dec()

        self.log.indent_inc( message = 'prepare driver'          )
        self.driver.prepare()
        self.log.indent_dec()
           
        self.log.indent_inc( message = 'open scope'              )
        self.scope.open()
        self.log.indent_dec()
   
        self.log.indent_inc( message = 'prepare scope'           )
        self._prepare_scope()
        self.log.indent_dec()
    
        sca3s_be.share.sys.relax()

        self.log.indent_inc( message = 'execute driver prologue' )
        self.driver.execute_prologue()
        self.log.indent_dec()
    
        sca3s_be.share.sys.relax()

        self.log.indent_inc( message = 'execute driver'          )
        self.driver.execute()
        self.log.indent_dec()
    
        sca3s_be.share.sys.relax()

        self.log.indent_inc( message = 'execute driver epilogue' )
        self.driver.execute_epilogue()
        self.log.indent_dec()

        sca3s_be.share.sys.relax()

        self.log.indent_inc( message = 'dump driver outcome'     )
        self.log.info( 'transfer = %s' % ( str( self.result_transfer ) ) )
        self.log.info( 'response = %s' % ( str( self.result_response ) ) )
        self.log.indent_dec()

    except Exception as e :
      raise e

    finally :
      self.log.indent_rst()

      if ( self.depo  != None ) :
        self.log.indent_inc( message = 'transfer local -> depo.' )
        self.depo.transfer()
        self.log.indent_dec()

      if ( self.board != None ) :
        self.log.indent_inc( message = 'close board'             )
        self.board.close()
        self.log.indent_dec()

      if ( self.scope != None ) :
        self.log.indent_inc( message = 'close scope'             )
        self.scope.close()
        self.log.indent_dec()

  # Execute job epilogue.
  
  def execute_epilogue( self ) :
    pass
