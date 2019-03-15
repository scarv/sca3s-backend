# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share

import logging, logging.handlers, os, sys

class IndentAdapter( logging.LoggerAdapter ):
  def __init__( self, logger, args, indent = 0, replace = dict() ) :
    super().__init__( logger, args ) ; self.indent = indent ; self.replace = replace

  def shutdown( self ) :
    self.logger.disabled = True

    for handler in self.logger.handlers :
      handler.flush() ; handler.close() 

    self.logger.handlers.clear()
      
  def indent_inc( self, n = 1, level = logging.INFO, message = None ) :
    if ( message != None ) :
      self.log( level, message )

    self.indent = min( 10, self.indent + n )
      
  def indent_dec( self, n = 1, level = logging.INFO, message = None ) :
    self.indent = max(  0, self.indent - n )
      
    if ( message != None ) :
      self.log( level, message )

  def process( self, message, args ):
    for ( k, v ) in self.replace.items() :
      message.replace( k, v )

    return '{indent}{message}'.format( indent = '  ' * self.indent, message = message ), args

def build_log_sys( name = '', path = 'acquire.log' ) :
  logger = logging.getLogger( name )
  formatter = logging.Formatter( '[%(asctime)s]: %(message)s', datefmt = '%d/%m/%y @ %H:%M:%S' )

  handler = logging.StreamHandler( sys.stdout )
  handler.setFormatter( formatter ) ; logger.addHandler( handler )

  handler = logging.handlers.RotatingFileHandler( os.path.join( share.sys.conf.get( 'log', section = 'path' ), path ), maxBytes = 1 << 20, backupCount = 100 )
  handler.setFormatter( formatter ) ; logger.addHandler( handler )

  debug = int( share.sys.conf.get( 'debug', section = 'sys' ) )

  if   ( debug == 0 ) :
    logger.setLevel( logging.INFO  )
  elif ( debug >  0 ) :
    logger.setLevel( logging.DEBUG )

  return IndentAdapter( logger, {}, indent = 0 )

def build_log_job( name = '', path =     'job.log' ) :
  logger = logging.getLogger( name )
  formatter = logging.Formatter( '[%(asctime)s]: %(message)s', datefmt = '%d/%m/%y @ %H:%M:%S' )

  handler = logging.FileHandler( path )
  handler.setFormatter( formatter ) ; logger.addHandler( handler )

  logger.setLevel( logging.INFO )

  return IndentAdapter( logger, {}, indent = 0, replace = { os.getcwd() : '${JOB}', os.path.basename( os.getcwd() ) : '${JOB}' } )
