# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import abc, docker, os, subprocess

class JobAbs( abc.ABC ) :
  def __init__( self, conf, path, log ) :
    super().__init__()  

    self.conf    = conf

    self.path    = path
    self.log     = log

  def _drain( self, id, lines ) :
    lines = lines.decode().split( '\n' )
      
    if ( ( len( lines ) > 0 ) and ( lines[ -1 ] == '' ) ) :
      lines.pop()
      
    for line in lines :
      self.log.info( '< %s : %s', id, line )

  def exec_native( self, cmd, env = None, timeout = None ) :
    if ( env     == None ) :
      env     =      sca3s_be.share.sys.conf.get( 'env',     section = 'run' )
    if ( timeout == None ) :
      timeout = int( sca3s_be.share.sys.conf.get( 'timeout', section = 'run' ) )

    env = { **os.environ, **env }

    if ( not quiet ) :
      self.log.indent_inc( message = 'execute' )

    if ( not quiet ) :
      self.log.info( '| cmd : %s', str( cmd ) )

    sca3s_be.share.sys.log.debug( '! env     : %s', str( env     ) )
    sca3s_be.share.sys.log.debug( '! timeout : %s', str( timeout ) )
    sca3s_be.share.sys.log.debug( '! quiet   : %s', str( quiet   ) )
    sca3s_be.share.sys.log.debug( '! fail    : %s', str( fail    ) )

    try :
      pd = subprocess.run( cmd, cwd = self.path, env = env, timeout = timeout, stdout = subprocess.PIPE, stderr = subprocess.PIPE )

      if ( not quiet ) :
        self._drain( 'stdout', pd.stdout )
        self._drain( 'stderr', pd.stderr )

      result = pd.returncode ; result_str = 'success' if ( result == 0 ) else 'failure'

    except subprocess.TimeoutExpired :
      result =            -1 ; result_str = 'timeout'

    if ( not quiet ) :    
      self.log.info( '| result : %s (exit status = %d)', result_str, result )

    if ( not quiet ) :
      self.log.indent_dec()

    if ( ( fail == True ) and ( result != 0 ) ) :
      raise Exception( 'failed to complete command execution' )

    return ( result == 0 )

  def exec_docker( self, cmd, env = None, vol = None ) :
    if ( env == None ) :
      env = dict()
    if ( vol == None ) :
      vol = dict()

    image = 'scarv' + '/' + 'sca3s-harness' + '.' + self.conf.get( 'board_id' ).replace( '/', '-' ) + ':' + sca3s_be.share.version.VERSION

    env.update( { 'DOCKER_GID' : os.getgid() } )
    env.update( { 'DOCKER_UID' : os.getuid() } )

    env.update( {    'CONTEXT' : 'native'                                                                                            } )
    env.update( {      'BOARD' : self.conf.get(  'board_id' )                                                                        } ) 
    env.update( {     'KERNEL' : self.conf.get( 'driver_id' )                                                                        } )
    env.update( {       'CONF' : ' '.join( [ '-D' + str( k ) + '=' + '"' + str( v ) + '"' for ( k, v ) in self.repo.conf.items() ] ) } )

    vol.update( { os.path.join( self.path, 'target' ) : { 'bind' : '/mnt/scarv/sca3s/harness', 'mode' : 'rw' } } )

    self.log.info( 'docker image       = %s', image )
    self.log.info( 'docker environment = %s', env   )
    self.log.info( 'docker volume      = %s', vol   )

    self.log.indent_inc( message = 'docker build context => %s' % ( cmd ) )
    self._drain( 'stdout', docker.from_env().containers.run( image, command = cmd, environment = env, volumes = vol, privileged = False, detach = False, auto_remove = True, stdout = True, stderr = True ) )
    self.log.indent_dec()

  @abc.abstractmethod
  def process_prologue( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def process( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def process_epilogue( self ) :
    raise NotImplementedError()
