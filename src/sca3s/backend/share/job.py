# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend as be
from sca3s import share   as share

import abc, os, subprocess

class JobAbs( abc.ABC ) :
  def __init__( self, conf, path, log ) :
    super().__init__()  

    self.conf    = conf

    self.path    = path
    self.log     = log

  def drain( self, id, lines ) :
    lines = lines.decode().split( '\n' )
      
    if ( ( len( lines ) > 0 ) and ( lines[ -1 ] == '' ) ) :
      lines.pop()
      
    for line in lines :
      self.log.info( '< %s : %s', id, line )

  def run( self, cmd, env = None, timeout = None, quiet = False, fail = True ) :
    if ( env     == None ) :
      env     =      be.share.sys.conf.get( 'env',     section = 'run' )
    if ( timeout == None ) :
      timeout = int( be.share.sys.conf.get( 'timeout', section = 'run' ) )

    env = { **os.environ, **env }

    if ( not quiet ) :
      self.log.indent_inc( message = 'execute' )

    if ( not quiet ) :
      self.log.info( '| cmd : %s', str( cmd ) )

    be.share.sys.log.debug( '! env     : %s', str( env     ) )
    be.share.sys.log.debug( '! timeout : %s', str( timeout ) )
    be.share.sys.log.debug( '! quiet   : %s', str( quiet   ) )
    be.share.sys.log.debug( '! fail    : %s', str( fail    ) )

    try :
      pd = subprocess.run( cmd, cwd = self.path, env = env, timeout = timeout, stdout = subprocess.PIPE, stderr = subprocess.PIPE )

      if ( not quiet ) :
        self.drain( 'stdout', pd.stdout )
        self.drain( 'stderr', pd.stderr )

      result = pd.returncode ; result_str = 'success' if ( result == 0 ) else 'failure'

    except subprocess.TimeoutExpired :
      result =            -1 ; result_str = 'timeout'

    if ( not quiet ) :    
      self.log.info( '| result : %s (exit status = %d)', result_str, result )

    if ( not quiet ) :
      self.log.indent_dec()

    if ( ( fail == True ) and ( result != 0 ) ) :
      raise Exception()

    return ( result == 0 )

  @abc.abstractmethod
  def process_prologue( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def process( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def process_epilogue( self ) :
    raise NotImplementedError()
