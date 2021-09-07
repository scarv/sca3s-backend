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

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import binascii, struct

class DriverImp( driver.block.DriverType ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.tvla_s_0 = None
    self.tvla_s_1 = None

  def _policy_tvla_init_lhs( self, spec             ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if   ( self.job.board.kernel_id_modeof == 'enc' ) :
      sizeof_k = self.job.board.kernel_data_wr_size[ 'k' ]
      sizeof_x = self.job.board.kernel_data_wr_size[ 'm' ]
    elif ( self.job.board.kernel_id_modeof == 'dec' ) :
      sizeof_k = self.job.board.kernel_data_wr_size[ 'k' ]
      sizeof_x = self.job.board.kernel_data_wr_size[ 'c' ]

    if  ( tvla_mode == 'fvr_k' ) :
      if   ( sizeof_k == 16 ) :
        k =                                        bytes( binascii.a2b_hex( '811E3731B0120A7842781E22B25CDDF9'                                 ) )
        x =                                        bytes( binascii.a2b_hex( 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'                                 ) )
      elif ( sizeof_k == 24 ) :
        k =                                        bytes( binascii.a2b_hex( '811E3731B0120A7842781E22B25CDDF994F4D92CD2FAE645'                 ) )
        x =                                        bytes( binascii.a2b_hex( 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'                                 ) )
      elif ( sizeof_k == 32 ) :
        k =                                        bytes( binascii.a2b_hex( '811E3731B0120A7842781E22B25CDDF994F4D92CD2FAE64537B940EA5E1AF112' ) )
        x =                                        bytes( binascii.a2b_hex( 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'                                 ) )

    elif( tvla_mode == 'fvr_d' ) :
      if   ( sizeof_k == 16 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x =                                        bytes( binascii.a2b_hex( 'DA39A3EE5E6B4B0D3255BFEF95601890'                                 ) )
      elif ( sizeof_k == 24 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x =                                        bytes( binascii.a2b_hex( 'DA39A3EE5E6B4B0D3255BFEF95601888'                                 ) )
      elif ( sizeof_k == 32 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x =                                        bytes( binascii.a2b_hex( 'DA39A3EE5E6B4B0D3255BFEF95601895'                                 ) )

    elif( tvla_mode == 'svr_d' ) :
      if   ( sizeof_k == 16 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x = None
      elif ( sizeof_k == 24 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x = None
      elif ( sizeof_k == 32 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x = None

    elif( tvla_mode == 'rvr_d' ) :
      if   ( sizeof_k == 16 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x =                                        bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )
      elif ( sizeof_k == 24 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x =                                        bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )
      elif ( sizeof_k == 32 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x =                                        bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

    if   ( self.job.board.kernel_id_modeof == 'enc' ) :
      return { 'k' : k, 'm' : x }  
    elif ( self.job.board.kernel_id_modeof == 'dec' ) :
      return { 'k' : k, 'c' : x }  

  def _policy_tvla_init_rhs( self, spec             ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if   ( self.job.board.kernel_id_modeof == 'enc' ) :
      sizeof_k = self.job.board.kernel_data_wr_size[ 'k' ]
      sizeof_x = self.job.board.kernel_data_wr_size[ 'm' ]
    elif ( self.job.board.kernel_id_modeof == 'dec' ) :
      sizeof_k = self.job.board.kernel_data_wr_size[ 'k' ]
      sizeof_x = self.job.board.kernel_data_wr_size[ 'c' ]

    if  ( tvla_mode == 'fvr_k' ) :
      if   ( sizeof_k == 16 ) :
        self.tvla_s_0 =                            bytes( binascii.a2b_hex( '53535353535353535353535353535353'                                 ) )

        k = ( self.tvla_s_0                 )[ 0 : sizeof_k ]
        x =                                        bytes( binascii.a2b_hex( 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'                                 ) )

      elif ( sizeof_k == 24 ) :
        self.tvla_s_0 =                            bytes( binascii.a2b_hex( '53535353535353535353535353535353'                                 ) )
        self.tvla_s_1 = sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ) ).enc( self.tvla_s_0 )

        k = ( self.tvla_s_0 + self.tvla_s_1 )[ 0 : sizeof_k ]
        x =                                        bytes( binascii.a2b_hex( 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'                                 ) )

      elif ( sizeof_k == 32 ) :
        self.tvla_s_0 =                            bytes( binascii.a2b_hex( '53535353535353535353535353535353'                                 ) )
        self.tvla_s_1 = sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ) ).enc( self.tvla_s_0 )

        k = ( self.tvla_s_0 + self.tvla_s_1 )[ 0 : sizeof_k ]
        x =                                        bytes( binascii.a2b_hex( 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC'                                 ) )

    elif( tvla_mode == 'fvr_d' ) :
      if   ( sizeof_k == 16 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x =                                        bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )
      elif ( sizeof_k == 24 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x =                                        bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )
      elif ( sizeof_k == 32 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x =                                        bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

    elif( tvla_mode == 'svr_d' ) :
      if   ( sizeof_k == 16 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x =                                        bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )
      elif ( sizeof_k == 24 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x =                                        bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )
      elif ( sizeof_k == 32 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x =                                        bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

    elif( tvla_mode == 'rvr_d' ) :
      if   ( sizeof_k == 16 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) )
        x =                                        bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )
      elif ( sizeof_k == 24 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) )
        x =                                        bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )
      elif ( sizeof_k == 32 ) :
        k =                                        bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) )
        x =                                        bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) )

    if   ( self.job.board.kernel_id_modeof == 'enc' ) :
      return { 'k' : k, 'm' : x }  
    elif ( self.job.board.kernel_id_modeof == 'dec' ) :
      return { 'k' : k, 'c' : x }  

  def _policy_tvla_step_lhs( self, spec, n, i, data ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if   ( self.job.board.kernel_id_modeof == 'enc' ) :
      sizeof_k = self.job.board.kernel_data_wr_size[ 'k' ] ; k = data[ 'k' ]
      sizeof_x = self.job.board.kernel_data_wr_size[ 'm' ] ; x = data[ 'm' ]
    elif ( self.job.board.kernel_id_modeof == 'dec' ) :
      sizeof_k = self.job.board.kernel_data_wr_size[ 'k' ] ; k = data[ 'k' ]
      sizeof_x = self.job.board.kernel_data_wr_size[ 'c' ] ; x = data[ 'c' ]

    if  ( tvla_mode == 'fvr_k' ) :
      if   ( sizeof_k == 16 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ) ).enc( x )
      elif ( sizeof_k == 24 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ) ).enc( x )
      elif ( sizeof_k == 32 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ) ).enc( x )

    elif( tvla_mode == 'fvr_d' ) :
      k = k
      x = x

    elif( tvla_mode == 'svr_d' ) :
      k = k

      x = bytes( binascii.a2b_hex( '8B8A490BDF7C00BDD7E6066C61002412' ) ) ; i = struct.pack( '<I', i )
      x = bytes( [ a ^ b for ( a, b ) in zip( x[ 0 : 4 ], i[ 0 : 4 ] ) ] ) + x[ 4 : ]

      if   ( self.job.board.kernel_id_modeof == 'enc' ) :
        x = sca3s_be.share.crypto.AES( k ).enc_rev( x, tvla_round )
      elif ( self.job.board.kernel_id_modeof == 'dec' ) :
        x = sca3s_be.share.crypto.AES( k ).dec_rev( x, tvla_round )

    elif( tvla_mode == 'rvr_d' ) :
      if   ( sizeof_k == 16 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ) ).enc( x )
      elif ( sizeof_k == 24 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ) ).enc( x )
      elif ( sizeof_k == 32 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ) ).enc( x )

    if   ( self.job.board.kernel_id_modeof == 'enc' ) :
      return { 'k' : k, 'm' : x }  
    elif ( self.job.board.kernel_id_modeof == 'dec' ) :
      return { 'k' : k, 'c' : x }  

  def _policy_tvla_step_rhs( self, spec, n, i, data ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if   ( self.job.board.kernel_id_modeof == 'enc' ) :
      sizeof_k = self.job.board.kernel_data_wr_size[ 'k' ] ; k = data[ 'k' ]
      sizeof_x = self.job.board.kernel_data_wr_size[ 'm' ] ; x = data[ 'm' ]
    elif ( self.job.board.kernel_id_modeof == 'dec' ) :
      sizeof_k = self.job.board.kernel_data_wr_size[ 'k' ] ; k = data[ 'k' ]
      sizeof_x = self.job.board.kernel_data_wr_size[ 'c' ] ; x = data[ 'c' ]

    if  ( tvla_mode == 'fvr_k' ) :
      if   ( sizeof_k == 16 ) :
        self.tvla_s_0 = sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0                 )[ 0 : sizeof_k ]
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ) ).enc( x )

      elif ( sizeof_k == 24 ) :
        self.tvla_s_0 = sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_1 )
        self.tvla_s_1 = sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0 + self.tvla_s_1 )[ 0 : sizeof_k ]
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ) ).enc( x )

      elif ( sizeof_k == 32 ) :
        self.tvla_s_0 = sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_1 )
        self.tvla_s_1 = sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0' ) ), self.tvla_s_0 )

        k = ( self.tvla_s_0 + self.tvla_s_1 )[ 0 : sizeof_k ]
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ) ).enc( x )

    elif( tvla_mode == 'fvr_d' ) :
      if   ( sizeof_k == 16 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ) ).enc( x )
      elif ( sizeof_k == 24 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ) ).enc( x )
      elif ( sizeof_k == 32 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ) ).enc( x )

    elif( tvla_mode == 'svr_d' ) :
      if   ( sizeof_k == 16 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ) ).enc( x )
      elif ( sizeof_k == 24 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ) ).enc( x )
      elif ( sizeof_k == 32 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ) ).enc( x )

    elif( tvla_mode == 'rvr_d' ) :
      if   ( sizeof_k == 16 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ) ).enc( x )
      elif ( sizeof_k == 24 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ) ).enc( x )
      elif ( sizeof_k == 32 ) :
        k = k
        x =             sca3s_be.share.crypto.AES( bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ) ).enc( x )

    if   ( self.job.board.kernel_id_modeof == 'enc' ) :
      return { 'k' : k, 'm' : x }  
    elif ( self.job.board.kernel_id_modeof == 'dec' ) :
      return { 'k' : k, 'c' : x }  

  def _supports_policy_user( self, spec ) :
    return True

  def _supports_policy_tvla( self, spec ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if  ( tvla_mode == 'fvr_k' ) :
      return True
    elif( tvla_mode == 'fvr_d' ) :
      return True
    elif( tvla_mode == 'svr_d' ) :
      return True
    elif( tvla_mode == 'rvr_d' ) :
      return True

    return False

  def _supports_verify( self ) :
    return True

  def _verify( self, data_wr, data_rd ) :
    if   ( self.job.board.kernel_id_modeof == 'enc' ) :
      return ( sca3s_be.share.crypto.AES( data_wr[ 'k' ] ).enc( data_wr[ 'm' ] ) ) == ( data_rd[ 'c' ] )
    elif ( self.job.board.kernel_id_modeof == 'dec' ) :
      return ( sca3s_be.share.crypto.AES( data_wr[ 'k' ] ).dec( data_wr[ 'c' ] ) ) == ( data_rd[ 'm' ] )

    return False
