# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend as be
from sca3s import share   as share

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import abc, binascii, random, re

class KernelType( kernel.KernelAbs ) :
  def __init__( self, func, sizeof_k, sizeof_r, sizeof_m, sizeof_c ) :
    super().__init__( func )

    self.sizeof_k = sizeof_k
    self.sizeof_r = sizeof_r
    self.sizeof_m = sizeof_m
    self.sizeof_c = sizeof_c

  @abc.abstractmethod
  def enc( self, k, m ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def dec( self, k, c ) :
    raise NotImplementedError()

  def value( self, x ) :
    r = ''
  
    for t in re.split( '({[^}]*})', x ) :
      if ( ( not t.startswith( '{' ) ) or ( not t.endswith( '}' ) ) ) :
        r += t ; continue
    
      ( x, n ) = tuple( t.strip( '{}' ).split( '*' ) )
    
      x = x.strip()
      n = n.strip()
  
      if   ( n == '|k|' ) :
        r += x * ( 2 * self.sizeof_k )
      elif ( n == '|r|' ) :
        r += x * ( 2 * self.sizeof_r )
      elif ( n == '|m|' ) :
        r += x * ( 2 * self.sizeof_m )
      elif ( n == '|c|' ) :
        r += x * ( 2 * self.sizeof_c )
      else :
        r += x * int( n )

    return bytes( binascii.a2b_hex( ''.join( [ ( '%X' % random.getrandbits( 4 ) ) if ( r[ i ] == '$' ) else ( r[ i ] ) for i in range( len( r ) ) ] ) ) )

  def policy_user_init( self, spec ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    if   ( self.func == 'enc' ) :
      k = self.value( user_value.get( 'k' ) )
      x = self.value( user_value.get( 'm' ) )
    elif ( self.func == 'dec' ) :
      k = self.value( user_value.get( 'k' ) )
      c = self.value( user_value.get( 'c' ) )

    return ( k, x )

  def policy_user_iter( self, spec, k, x, i ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    if   ( self.func == 'enc' ) :
      k = self.value( user_value.get( 'k' ) ) if ( user_select.get( 'k' ) == 'each' ) else ( k )
      x = self.value( user_value.get( 'm' ) ) if ( user_select.get( 'm' ) == 'each' ) else ( x )
    elif ( self.func == 'dec' ) :
      k = self.value( user_value.get( 'k' ) ) if ( user_select.get( 'k' ) == 'each' ) else ( k )
      x = self.value( user_value.get( 'c' ) ) if ( user_select.get( 'c' ) == 'each' ) else ( x )

    return ( k, x )

  @abc.abstractmethod
  def policy_tvla_init_lhs( self, spec ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def policy_tvla_iter_lhs( self, spec, k, x, i ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def policy_tvla_init_rhs( self, spec ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def policy_tvla_iter_rhs( self, spec, k, x, i ) :
    raise NotImplementedError()
