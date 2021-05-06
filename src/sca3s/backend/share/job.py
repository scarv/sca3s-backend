# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import abc, docker, os, requests, subprocess

class JobAbs( abc.ABC ) :
  def __init__( self, conf, path, log ) :
    super().__init__()  

    self.conf            = conf

    self.path            = path
    self.log             =  log

    self.job_type        = self.conf.get( 'job_type'    )
    self.job_id          = self.conf.get( 'job_id'      )
    self.job_version     = self.conf.get( 'job_version' )

    self.result_transfer = dict()
    self.result_response = dict()

  def _drain( self, id, lines ) :
    lines = lines.decode().split( '\n' )
      
    if ( ( len( lines ) > 0 ) and ( lines[ -1 ] == '' ) ) :
      lines.pop()
      
    for line in lines :
      self.log.info( '< %s : %s', id, line )

  def exec_native( self, cmd, env = None,             timeout = None, quiet = False ) :
    if ( env     == None ) :
      env     = dict( sca3s_be.share.sys.conf.get( 'env',     section = 'exec_native' ) )
    if ( timeout == None ) :
      timeout =  int( sca3s_be.share.sys.conf.get( 'timeout', section = 'exec_native' ) )

    env = { **os.environ, **env }

    # execute prologue
    if ( not quiet ) :
      self.log.indent_inc( message = 'execute (native) => %s' % ( cmd ) )

    sca3s_be.share.sys.log.debug( '! cmd     = %s', str( cmd     ) )
    sca3s_be.share.sys.log.debug( '! env     = %s', str( env     ) )
    sca3s_be.share.sys.log.debug( '! timeout = %s', str( timeout ) )
    sca3s_be.share.sys.log.debug( '! quiet   = %s', str( quiet   ) )

    # execute
    try :
      pd = subprocess.run( cmd, cwd = self.path, env = env, timeout = timeout, stdout = subprocess.PIPE, stderr = subprocess.PIPE )

      if ( not quiet ) :
        self._drain( 'stdout', pd.stdout )
        self._drain( 'stderr', pd.stderr )

      result = pd.returncode          ; result_str = 'success' if ( result == 0 ) else 'failure'

    except subprocess.TimeoutExpired :
      result =  -1                    ; result_str = 'timeout'

    # execute epilogue
    if ( not quiet ) :    
      self.log.info( '| result : %s (exit status = %d)', result_str, result )

    if ( not quiet ) :
      self.log.indent_dec()

    if ( result != 0 ) :
      raise Exception( 'failed (native) command execution' )

    return result

  def exec_docker( self, cmd, env = None, vol = None, timeout = None, quiet = False ) :
    if ( env     == None ) :
      env     = dict( sca3s_be.share.sys.conf.get( 'env',     section = 'exec_docker' ) )
    if ( vol     == None ) :
      vol     = dict( sca3s_be.share.sys.conf.get( 'vol',     section = 'exec_docker' ) )
    if ( timeout == None ) :
      timeout =  int( sca3s_be.share.sys.conf.get( 'timeout', section = 'exec_docker' ) )

    image = 'scarv' + '/' + 'sca3s-harness' + '.' + self.conf.get( 'board_id' ).replace( '/', '-' ) + ':' + sca3s_be.share.version.ident()

    # board-specific environment
    env.update( self.board.get_docker_env() )
    # board-agnostic environment
    env.update( { 'DOCKER_GID' : os.getgid()                  } )
    env.update( { 'DOCKER_UID' : os.getuid()                  } )

    env.update( {    'CONTEXT' : 'native'                     } )
    env.update( {      'BOARD' : self.conf.get(  'board_id' ) } ) 
    env.update( {     'KERNEL' : self.conf.get( 'driver_id' ) } )

    # board-specific volume
    vol.update( self.board.get_docker_vol() )
    # board-agnostic volume
    vol.update( { os.path.join( self.path, 'target' ) : { 'bind' : '/mnt/scarv/sca3s/harness', 'mode' : 'rw' } } )

    # board configuration
    env[ 'CONF' ] = ( ' '.join( self.repo.conf + self.board.get_docker_conf() ) ).strip()

    # execute prologue

    if ( not quiet ) :
      self.log.indent_inc( message = 'execute (docker) => %s' % ( cmd ) )

    sca3s_be.share.sys.log.debug( '! cmd     = %s', str( cmd     ) )
    sca3s_be.share.sys.log.debug( '! env     = %s', str( env     ) )
    sca3s_be.share.sys.log.debug( '! vol     = %s', str( vol     ) )
    sca3s_be.share.sys.log.debug( '! timeout = %s', str( timeout ) )
    sca3s_be.share.sys.log.debug( '! quiet   = %s', str( quiet   ) )
    sca3s_be.share.sys.log.debug( '! image   = %s', str( image   ) )

    # execute

    try :
      cd = docker.from_env().containers.run( image, command = cmd, environment = env, volumes = vol, privileged = False, network_disabled = True, detach = True, stdout = True, stderr = True )
    
      status = cd.wait() if ( True ) else cd.wait( timeout = timeout )

      if ( not quiet ) :    
        self._drain( 'stdout', cd.logs( stdout =  True, stderr = False ) )
        self._drain( 'stderr', cd.logs( stdout = False, stderr =  True ) )
    
      cd.remove()

      result = status[ 'StatusCode' ] ; result_str = 'success' if ( result == 0 ) else 'failure'

    except requests.exceptions.ReadTimeout :
      result = -1                     ; result_str = 'timeout'

    # execute epilogue

    if ( not quiet ) :    
      self.log.info( '| result : %s (exit status = %d)', result_str, result )

    if ( not quiet ) :
      self.log.indent_dec()

    if ( result != 0 ) :
      raise Exception( 'failed (docker) command execution' )

    return result

  @abc.abstractmethod
  def execute_prologue( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def execute( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def execute_epilogue( self ) :
    raise NotImplementedError()
