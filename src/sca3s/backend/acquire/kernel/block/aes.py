# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import hybrid as hybrid

from sca3s.backend.acquire import driver as driver
from sca3s.backend.acquire import kernel as kernel

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import binascii, struct

class KernelImp( kernel.block.KernelType ) :
  def __init__( self, nameof, typeof, data_wr_id, data_wr_size, data_rd_id, data_rd_size ) :
    super().__init__( nameof, typeof, data_wr_id, data_wr_size, data_rd_id, data_rd_size )

    self.tvla_s_0 = None
    self.tvla_s_1 = None

  def supports_kernel( self    ) :
    return True

  def supports_policy( self, x ) :
    if   ( x == 'user' ) :
      return True
    elif ( x == 'tvla' ) :
      return True

    return False

  def kernel_enc( self, k, m ) :
    return sca3s_be.share.crypto.AES( k ).enc( m )

  def kernel_dec( self, k, c ) :
    return sca3s_be.share.crypto.AES( k ).dec( c )

  def policy_tvla_init_lhs( self, spec             ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if  ( tvla_mode == 'fvr_k' ) :
      if   ( self.sizeof_k == 16 ) :
        k =                  bytes( binascii.a2b_hex( '811E3731B0120A7842781E22B25CDDF9'                                 ) )
        x =                  bytes( binascii.a2b_hex( 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        k =                  bytes( binascii.a2b_hex( '811E3731B0120A7842781E22B25CDDF994F4D92CD2FAE645'                 ) )
        x =                  bytes( binascii.a2b_hex( 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        k =                  bytes( binascii.a2b_hex( '811E3731B0120A7842781E22B25CDDF994F4D92CD2FAE64537B940EA5E1AF112' ) )
        x =                  bytes( binascii.a2b_hex( 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'                                 ) )

    elif( tvla_mode == 'fvr_d' ) :
      if   ( self.sizeof_k == 16 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x =                  bytes( binascii.a2b_hex( 'DA39A3EE5E6B4B0D3255BFEF95601890'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x =                  bytes( binascii.a2b_hex( 'DA39A3EE5E6B4B0D3255BFEF95601888'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x =                  bytes( binascii.a2b_hex( 'DA39A3EE5E6B4B0D3255BFEF95601895'                                 ) )

    elif( tvla_mode == 'svr_d' ) :
      if   ( self.sizeof_k == 16 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x = None

      elif ( self.sizeof_k == 24 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x = None

      elif ( self.sizeof_k == 32 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x = None

    elif( tvla_mode == 'rvr_d' ) :
      if   ( self.sizeof_k == 16 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x =                  bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x =                  bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x =                  bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

    return ( k, x )

  def policy_tvla_iter_lhs( self, spec, n, i, k, x ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if  ( tvla_mode == 'fvr_k' ) :
      if   ( self.sizeof_k == 16 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ), x )

      elif ( self.sizeof_k == 24 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ), x )

      elif ( self.sizeof_k == 32 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ), x )

    elif( tvla_mode == 'fvr_d' ) :
      k = k
      x = x

    elif( tvla_mode == 'svr_d' ) :
      k = k

      x = bytes( binascii.a2b_hex( '8B8A490BDF7C00BDD7E6066C61002412' ) ) ; i = struct.pack( '<I', i )
      x = bytes( [ a ^ b for ( a, b ) in zip( x[ 0 : 4 ], i[ 0 : 4 ] ) ] ) + x[ 4 : ]

      if   ( self.typeof == 'enc' ) :
        x = sca3s_be.share.crypto.AES( k ).enc_rev( x, tvla_round )
      elif ( self.typeof == 'dec' ) :
        x = sca3s_be.share.crypto.AES( k ).dec_rev( x, tvla_round )

    elif( tvla_mode == 'rvr_d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ), x )

      elif ( self.sizeof_k == 24 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ), x )

      elif ( self.sizeof_k == 32 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ), x )

    return ( k, x )

  def policy_tvla_init_rhs( self, spec             ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if  ( tvla_mode == 'fvr_k' ) :
      if   ( self.sizeof_k == 16 ) :
        self.tvla_s_0 =                  bytes( binascii.a2b_hex( '53535353535353535353535353535353' ) )

        k = ( self.tvla_s_0                 )[ 0 : self.sizeof_k ]
        x =                  bytes( binascii.a2b_hex( 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        self.tvla_s_0 =                  bytes( binascii.a2b_hex( '53535353535353535353535353535353' ) )
        self.tvla_s_1 = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0 + self.tvla_s_1 )[ 0 : self.sizeof_k ]
        x =                  bytes( binascii.a2b_hex( 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        self.tvla_s_0 =                  bytes( binascii.a2b_hex( '53535353535353535353535353535353' ) )
        self.tvla_s_1 = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0 + self.tvla_s_1 )[ 0 : self.sizeof_k ]
        x =                  bytes( binascii.a2b_hex( 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'                                 ) )

    elif( tvla_mode == 'fvr_d' ) :
      if   ( self.sizeof_k == 16 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x =                  bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x =                  bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x =                  bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

    elif( tvla_mode == 'svr_d' ) :
      if   ( self.sizeof_k == 16 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x =                  bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x =                  bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x =                  bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

    elif( tvla_mode == 'rvr_d' ) :
      if   ( self.sizeof_k == 16 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x =                  bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 24 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x =                  bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

      elif ( self.sizeof_k == 32 ) :
        k =                  bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x =                  bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

    return ( k, x )

  def policy_tvla_iter_rhs( self, spec, n, i, k, x ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if  ( tvla_mode == 'fvr_k' ) :
      if   ( self.sizeof_k == 16 ) :
        self.tvla_s_0 = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0                 )[ 0 : self.sizeof_k ]
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ), x )

      elif ( self.sizeof_k == 24 ) :
        self.tvla_s_0 = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_1 )
        self.tvla_s_1 = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0 + self.tvla_s_1 )[ 0 : self.sizeof_k ]
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ), x )

      elif ( self.sizeof_k == 32 ) :
        self.tvla_s_0 = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_1 )
        self.tvla_s_1 = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0 + self.tvla_s_1 )[ 0 : self.sizeof_k ]
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ), x )

    elif( tvla_mode == 'fvr_d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ), x )

      elif ( self.sizeof_k == 24 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ), x )

      elif ( self.sizeof_k == 32 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ), x )

    elif( tvla_mode == 'svr_d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ), x )

      elif ( self.sizeof_k == 24 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ), x )

      elif ( self.sizeof_k == 32 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ), x )

    elif( tvla_mode == 'rvr_d' ) :
      if   ( self.sizeof_k == 16 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ), x )

      elif ( self.sizeof_k == 24 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ), x )

      elif ( self.sizeof_k == 32 ) :
        k = k
        x = self.kernel_enc( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ), x )

    return ( k, x )
