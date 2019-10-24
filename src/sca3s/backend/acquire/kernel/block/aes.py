# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend as be
from sca3s import spec    as spec

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

from .                     import *

import binascii, Crypto.Cipher.AES as AES

class KernelImp( Block ) :
  def __init__( self, sizeof_k, sizeof_r, sizeof_m, sizeof_c ) :
    super().__init__( sizeof_k, sizeof_r, sizeof_m, sizeof_c )

    self.tvla_s_0 = None
    self.tvla_s_1 = None

  def supports( self, policy ) :
    if   ( policy == 'user' ) :
      return True
    elif ( policy == 'tvla' ) :
      return True

    return False

  def enc( self, k, m ) :
    return AES.new( k ).encrypt( m )

  def dec( self, k, c ) :
    return AES.new( k ).decrypt( m )

  def tvla_lhs_init( self, mode ) :
    if  ( mode == 'fvr-k' ) :
      if   ( self.sizeof_k == 16 ) :
        k = bytes( binascii.a2b_hex( '811E3731B0120A7842781E22B25CDDF9'                                 ) )
        x = bytes( binascii.a2b_hex( 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        k = bytes( binascii.a2b_hex( '811E3731B0120A7842781E22B25CDDF994F4D92CD2FAE645'                 ) )
        x = bytes( binascii.a2b_hex( 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        k = bytes( binascii.a2b_hex( '811E3731B0120A7842781E22B25CDDF994F4D92CD2FAE64537B940EA5E1AF112' ) )
        x = bytes( binascii.a2b_hex( 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'                                 ) )

    elif( mode == 'fvr-d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x = bytes( binascii.a2b_hex( 'DA39A3EE5E6B4B0D3255BFEF95601890'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x = bytes( binascii.a2b_hex( 'DA39A3EE5E6B4B0D3255BFEF95601888'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x = bytes( binascii.a2b_hex( 'DA39A3EE5E6B4B0D3255BFEF95601895'                                 ) )

    elif( mode == 'svr-d' ) :
      pass # TODO

    elif( mode == 'rvr-d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x = bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x = bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x = bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

    return ( k, x )

  def tvla_rhs_init( self, mode ) :
    if  ( mode == 'fvr-k' ) :
      if   ( self.sizeof_k == 16 ) :
        self.tvla_s_0 =           bytes( binascii.a2b_hex( '53535353535353535353535353535353' ) )

        k = ( self.tvla_s_0                 )[ 0 : self.sizeof_k ]
        x = bytes( binascii.a2b_hex( 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        self.tvla_s_0 =           bytes( binascii.a2b_hex( '53535353535353535353535353535353' ) )
        self.tvla_s_1 = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0 + self.tvla_s_1 )[ 0 : self.sizeof_k ]
        x = bytes( binascii.a2b_hex( 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        self.tvla_s_0 =           bytes( binascii.a2b_hex( '53535353535353535353535353535353' ) )
        self.tvla_s_1 = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0 + self.tvla_s_1 )[ 0 : self.sizeof_k ]
        x = bytes( binascii.a2b_hex( 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'                                 ) )

    elif( mode == 'fvr-d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x = bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x = bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x = bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

    elif( mode == 'svr-d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x = bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x = bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x = bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

    elif( mode == 'rvr-d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x = bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x = bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        k = bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x = bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

    return ( k, x )

  def tvla_lhs_step( self, mode, k, x ) :
    if  ( mode == 'fvr-k' ) :
      if   ( self.sizeof_k == 16 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ), x )

      elif ( self.sizeof_k == 24 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ), x )

      elif ( self.sizeof_k == 32 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ), x )

    elif( mode == 'fvr-d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = k
        x = x

      elif ( self.sizeof_k == 24 ) :
        k = k
        x = x

      elif ( self.sizeof_k == 32 ) :
        k = k
        x = x

    elif( mode == 'svr-d' ) :
      pass # TODO

    elif( mode == 'rvr-d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ), x )

      elif ( self.sizeof_k == 24 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ), x )

      elif ( self.sizeof_k == 32 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ), x )

    return ( k, x )

  def tvla_rhs_step( self, mode, k, x ) :
    if  ( mode == 'fvr-k' ) :
      if   ( self.sizeof_k == 16 ) :
        self.tvla_s_0 = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0                 )[ 0 : self.sizeof_k ]
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ), x )

      elif ( self.sizeof_k == 24 ) :
        self.tvla_s_0 = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_1 )
        self.tvla_s_1 = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0 + self.tvla_s_1 )[ 0 : self.sizeof_k ]
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ), x )

      elif ( self.sizeof_k == 32 ) :
        self.tvla_s_0 = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_1 )
        self.tvla_s_1 = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0 + self.tvla_s_1 )[ 0 : self.sizeof_k ]
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ), x )

    elif( mode == 'fvr-d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ), x )

      elif ( self.sizeof_k == 24 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ), x )

      elif ( self.sizeof_k == 32 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ), x )

    elif( mode == 'svr-d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ), x )

      elif ( self.sizeof_k == 24 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ), x )

      elif ( self.sizeof_k == 32 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ), x )

    elif( mode == 'rvr-d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ), x )

      elif ( self.sizeof_k == 24 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ), x )

      elif ( self.sizeof_k == 32 ) :
        k = k
        x = self.enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ), x )

    return ( k, x )
