# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import os

MAJOR = 0x01
MINOR = 0x02
PATCH = 0x04

def ident(              pattern = MAJOR | MINOR | PATCH ) :
  x = []

  x.append( str( sca3s_be.share.sys.conf.get( 'major', section = 'version' ) ) if ( pattern & MAJOR ) else '0' )
  x.append( str( sca3s_be.share.sys.conf.get( 'minor', section = 'version' ) ) if ( pattern & MINOR ) else '0' )
  x.append( str( sca3s_be.share.sys.conf.get( 'patch', section = 'version' ) ) if ( pattern & PATCH ) else '0' )

  return '.'.join( x )

def match( x, y = None, pattern = MAJOR | MINOR         ) :
  if ( y == None ) :
    y = ident()

  x = x.split( '.' )
  y = y.split( '.' )

  if ( ( pattern & MAJOR ) and ( x[ 0 ] != y[ 0 ] ) ) :
    return False
  if ( ( pattern & MINOR ) and ( x[ 1 ] != y[ 1 ] ) ) :
    return False
  if ( ( pattern & PATCH ) and ( x[ 2 ] != y[ 2 ] ) ) :
    return False

  return True
