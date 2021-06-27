# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import binascii, hashlib, numpy, random, re

def str2seq( x ) :
  return        [ ord( t ) for t in x ]

def seq2str( x ) :
  return bytes( [      t   for t in x ] )

LE = +1 ; BE = -1

def int2seq( x, b, endian = LE, pad = None ) :
  t = []

  while ( x != 0 ) :
    if   ( endian == LE ) : 
      t = t + [ x % b ]
    elif ( endian == BE ) : 
      t = [ x % b ] + t

    x = x // b

  if ( ( pad != None ) and ( len( t ) < pad ) ) :
    if   ( endian == LE ) : 
      t = t + ( [ 0 ] * ( pad - len( t ) ) )
    elif ( endian == BE ) : 
      t = ( [ 0 ] * ( pad - len( t ) ) ) + t

  return t

def seq2int( x, b, endian = LE ) :
  if   ( endian == LE ) :
    x = enumerate(           x   )
  elif ( endian == BE ) :
    x = enumerate( reversed( x ) )

  return sum( [ t * ( b ** i ) for ( i, t ) in x ] )

def octetstr2str( x ) :
  t = x.split( ':' ) ; n = int( t[ 0 ], 16 ) ; x = binascii.a2b_hex( t[ 1 ] )

  if( n != len( x ) ) :
    raise ValueError
  else :
    return x

def str2octetstr( x ) :
  return ( '%02X' % ( len( x ) ) ) + ':' + ( binascii.b2a_hex( x ).decode() )

def octetstr2int( x ) :
  return seq2int( octetstr2str( x ), 2 ** 8 )

def int2octetstr( x ) :
  return str2octetstr( seq2str( int2seq( x, 2 ** 8 ) ) )

def closest( xs, x ) :
  return min( xs, key = lambda t : abs( t - x ) )

def resize( xs, n, dtype = numpy.dtype( int ) ) :
  if   ( len( xs ) <  n ) :
    return numpy.concatenate( ( xs[ 0 :   ], numpy.array( [ 0 ] * ( n - len( xs ) ), dtype = dtype ) ) )
  elif ( len( xs ) >  n ) :
    return                      xs[ 0 : n ]
  elif ( len( xs ) == n ) :
    return                      xs

MEASURE_MODE_DURATION    = 0
MEASURE_MODE_TRIGGER_POS = 1
MEASURE_MODE_TRIGGER_NEG = 2

def measure( mode, samples, threshold ) :
  done = False ; edge_pos = 0; edge_neg = len( samples ) - 1

  for ( i, sample ) in enumerate( samples ) :
    if ( ( not done ) and ( sample > threshold ) ) :
      done =  True ; edge_pos = i
    if ( (     done ) and ( sample < threshold ) ) :
      done = False ; edge_neg = i ; break

  if   ( mode == MEASURE_MODE_DURATION    ) :
    return edge_neg - edge_pos + 1
  elif ( mode == MEASURE_MODE_TRIGGER_POS ) :
    return            edge_pos
  elif ( mode == MEASURE_MODE_TRIGGER_NEG ) :
    return edge_neg

def value( x, ns = dict() ) :
  if   ( type( x ) == bytes ) :
    return x
  elif ( type( x ) == str   ) :
    r = ''
    
    for t in re.split( '({[^}]*})', x ) :
      if ( ( not t.startswith( '{' ) ) or  ( not t.endswith( '}' ) ) ) :
        r += t ; continue
      
      ( x, n ) = tuple( t.strip( '{}' ).split( '*' ) )
      
      x = x.strip()
      n = n.strip()
    
      if ( (     n.startswith( '|' ) ) and (     n.endswith( '|' ) ) ) :
        if ( n.strip( '|' ) in ns ) :
          r += x * ( 2 * ns[ n.strip( '|' ) ] )
        else :
          r += x * int( n )
      else :
          r += x * int( n )
  
    return bytes( binascii.a2b_hex( ''.join( [ ( '%X' % random.getrandbits( 4 ) ) if ( r[ i ] == '$' ) else ( r[ i ] ) for i in range( len( r ) ) ] ) ) )

  return None
