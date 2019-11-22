# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import sys, traceback

def dump( exception, log = None ) :
  lines = list()

  for line in traceback.format_exception( *sys.exc_info() ) :
    lines.extend( line.strip( '\n' ).split( '\n' ) )

  n = max( [ len( line ) for line in lines ] )

  log.error( '┌' + ( '─' * ( n + 2 ) ) + '┐' )

  for line in lines :
    log.error( '│ ' + line + ( ' ' * ( n - len( line ) ) ) + ' │' )

  log.error( '└' + ( '─' * ( n + 2 ) ) + '┘' )
