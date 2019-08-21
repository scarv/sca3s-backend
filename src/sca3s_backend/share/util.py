# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

import sca3s_backend as be
import sca3s_spec    as spec

import binascii, hashlib

def str2seq( x ) :
  return          [ ord( t ) for t in x ]

def seq2str( x ) :
  return ''.join( [ chr( t ) for t in x ] )

def octetstr2str( x ) :
  t = x.split( ':' ) ; n = int( t[ 0 ], 16 ) ; x = binascii.a2b_hex( t[ 1 ] )

  if( n != len( x ) ) :
    raise ValueError
  else :
    return x

def str2octetstr( x ) :
  return ( '%02X' % ( len( x ) ) ) + ':' + ( binascii.b2a_hex( x ).decode() )

LE = +1 ; BE = -1

def int2seq( x, b, endian = LE, pad = None ) :
  t = []

  while ( x != 0 ) :
    if   ( endian == LE ) : 
      t = t + [ x % b ]
    elif ( endian == BE ) : 
      t = [ x % b ] + t

    x = x / b

  if ( ( pad != None ) and ( len( t ) < pad ) ) :
    if   ( endian == LE ) : 
      t = t + ( [ 0 ] * ( pad - len( t ) ) )
    elif ( endian == BE ) : 
      t = ( [ 0 ] * ( pad - len( t ) ) ) + t

  return t

def seq2int( x, b, endian = +1 ) :
  if   ( endian == LE ) :
    x = enumerate(           x   )
  elif ( endian == BE ) :
    x = enumerate( reversed( x ) )

  return sum( [ t * ( b ** i ) for ( i, t ) in x ] )

def closest( x, xs ) :
  return min( xs, key = lambda t : abs( t - x ) )

def MD5( f ) :
  H = hashlib.md5() ; fd = open( f, 'rb' )
  
  while( True ) :
    data = fd.read( 2 ** 10 )
  
    if ( len( data ) == 0 ):
      break
    else :
      H.update( data )
  
  fd.close()
  
  return H.hexdigest()

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
    return edge_neg - edge_pos
  elif ( mode == MEASURE_MODE_TRIGGER_POS ) :
    return            edge_pos
  elif ( mode == MEASURE_MODE_TRIGGER_NEG ) :
    return edge_neg
