# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import art, cowpy, logging, logging.handlers, os, sys

TYPE_SYS = 0
TYPE_JOB = 1

class LogAdapter( logging.LoggerAdapter ):
  def __init__( self, logger, args, indent = 0, redact = dict() ) :
    super().__init__( logger, args ) ; self.indent = indent ; self.redact = redact

  def shutdown( self ) :
    self.logger.disabled = True

    for handler in self.logger.handlers :
      handler.flush() ; handler.close() 

    self.logger.handlers.clear()

  def indent_rst( self, indent = 0 ) :
    self.indent = indent
      
  def indent_inc( self, level = logging.INFO, message = None, n = 1 ) :
    if ( message != None ) :
      self.log( level, message )

    self.indent = min( 10, self.indent + n )
      
  def indent_dec( self, level = logging.INFO, message = None, n = 1 ) :
    self.indent = max(  0, self.indent - n )
      
    if ( message != None ) :
      self.log( level, message )

  def banner( self, level = logging.INFO ) :
    n = 0 ; lines = art.text2art( 'SCA3S', font = 'assalt_m' )
  
    for line in lines.split( '\n' ) :
      line = line.rstrip()
    
      if ( line != '' ) :
        self.log( level, line ) ; n = max( n, len( line ) )
  
    self.log( level, '' )
    self.log( level, ( 'Side-Channel Analysis As A Service' ).center( n, ' ' ) )
    self.log( level, ( 'v' + sca3s_be.share.version.ident() ).center( n, ' ' ) )
    self.log( level, (     'https://sca3s.scarv.org'        ).center( n, ' ' ) )
    self.log( level, '' )
  
  def cowsay( self, message, level = logging.INFO, eyes = 'default', tongue = False ) :
    n = 0 ; lines = cow.Moose( eyes = eyes, tongue = tongue ).milk( message )
  
    for line in lines.split( '\n' ) :
      line = line.rstrip()
    
      if ( line != '' ) :
        self.log( level, line ) ; n = max( n, len( line ) )

  def log( self, level, message, *args, **kwargs ):
    if ( self.logger.isEnabledFor( level ) ) :  
      if ( self.redact != None ) :
        self.logger._log( level, self.redact( ( '|  ' * self.indent ) + message ), args )
      else :
        self.logger._log( level,            ( ( '|  ' * self.indent ) + message ), args )

# Enforcing, e.g., a uniform format, either build
#
# 1. a system logger object:
#
#    - output directs to file *and* console (i.e., stdout)
#    - output produced by adaptor that supports indentation and redactment
#    - threshold depends on debug option (e.g., can include information- and debug-level output)
#
# 2. a job    logger object:
#
#    - output directs to file
#    - output produced by adaptor that supports indentation and redactment
#    - threshold fixed to avoid any debug-level output
#
# in a given path, with a file name matching the task.

def build_log( type, path, id = None, redact = None ) :
  name = sca3s_be.share.sys.conf.get( 'task', section = 'sys' ) + '.log'

  logger = logging.getLogger( id )
  formatter = logging.Formatter( '[%(asctime)s] {%(name)s} : %(message)s', datefmt = '%d/%m/%y @ %H:%M:%S' )

  handler = logging.handlers.RotatingFileHandler( os.path.join( path, name ), maxBytes = 1 << 24, backupCount = 100 )
  handler.setFormatter( formatter )
  logger.addHandler( handler )

  if   ( type == TYPE_SYS ) :
    handler = logging.StreamHandler( sys.stdout )
    handler.setFormatter( formatter ) 
    logger.addHandler( handler )

    debug = int( sca3s_be.share.sys.conf.get( 'debug', section = 'sys' ) )

    if   ( debug == 0 ) :
      logger.setLevel( logging.INFO  )
    elif ( debug >  0 ) :
      logger.setLevel( logging.DEBUG )

  elif ( type == TYPE_JOB ) :
    logger.setLevel( logging.INFO )

  return LogAdapter( logger, {}, indent = 0, redact = redact )
