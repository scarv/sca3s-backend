# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share

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

MEASURE_MODE_EDGE_POS = 0
MEASURE_MODE_EDGE_NEG = 1
MEASURE_MODE_DURATION = 2

def measure( mode, samples, threshold ) :
  done = False ; edge_pos = 0; edge_neg = 0

  for ( i, sample ) in enumerate( samples ) :
    if ( ( not done ) and ( sample > threshold ) ) :
      done =  True ; edge_pos = i
    if ( (     done ) and ( sample < threshold ) ) :
      done = False ; edge_neg = i ; break

  if   ( mode == share.util.MEASURE_MODE_EDGE_POS ) :
    return            edge_pos
  elif ( mode == share.util.MEASURE_MODE_EDGE_NEG ) :
    return edge_neg
  elif ( mode == share.util.MEASURE_MODE_DURATION ) :
    return edge_neg - edge_pos
