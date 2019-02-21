# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire        import share  as share

from acquire.device import board  as board
from acquire.device import scope  as scope
from acquire        import driver as driver

from acquire        import repo   as repo
from acquire        import depo   as depo

import random

class DriverImp( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

  def _interact_enc( self ) :
    k = self.kernel_k
    r = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_r ) ] )
    m = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_m ) ] )

    if ( len( k ) > 0 ) :
      self.job.device_board.interact( '>reg k %s' % share.util.str2octetstr( k ).upper() )
    if ( len( r ) > 0 ) :
      self.job.device_board.interact( '>reg r %s' % share.util.str2octetstr( r ).upper() )
    if ( len( m ) > 0 ) :
      self.job.device_board.interact( '>reg m %s' % share.util.str2octetstr( m ).upper() )
  
    _                                  = self.job.device_scope.acquire( scope.ACQUIRE_MODE_PREPARE )

    self.job.device_board.interact( '!enc_init' )
    self.job.device_board.interact( '!enc'      )
  
    ( signal_trigger, signal_acquire ) = self.job.device_scope.acquire( scope.ACQUIRE_MODE_COLLECT )
  
    c = share.util.octetstr2str( self.job.device_board.interact( '<reg c' ) )

    tsc_enc = share.util.seq2int( share.util.octetstr2str( self.job.device_board.interact( '?tsc' ) ), 2 ** 8 )
    self.job.device_board.interact( '!nop'      )
    tsc_nop = share.util.seq2int( share.util.octetstr2str( self.job.device_board.interact( '?tsc' ) ), 2 ** 8 )

    return share.trace.Trace( signal_trigger, signal_acquire, tsc = tsc_enc - tsc_nop, data_i = { 'k' : k, 'r' : r, 'm' : m }, data_o = { 'c' : c } )

  def _interact_dec( self ) :
    k = self.kernel_k
    r = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_r ) ] )
    c = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_c ) ] )

    if ( len( k ) > 0 ) :
      self.job.device_board.interact( '>reg k %s' % share.util.str2octetstr( k ).upper() )
    if ( len( r ) > 0 ) :
      self.job.device_board.interact( '>reg r %s' % share.util.str2octetstr( r ).upper() )
    if ( len( c ) > 0 ) :
      self.job.device_board.interact( '>reg c %s' % share.util.str2octetstr( c ).upper() )
  
    _                                  = self.job.device_scope.acquire( scope.ACQUIRE_MODE_PREPARE )
  
    self.job.device_board.interact( '!dec_init' )
    self.job.device_board.interact( '!dec'      )
  
    ( signal_trigger, signal_acquire ) = self.job.device_scope.acquire( scope.ACQUIRE_MODE_COLLECT )
  
    m = share.util.octetstr2str( self.job.device_board.interact( '<reg m' ) )

    tsc_dec = share.util.seq2int( share.util.octetstr2str( self.job.device_board.interact( '?tsc' ) ), 2 ** 8 )
    self.job.device_board.interact( '!nop'      )
    tsc_nop = share.util.seq2int( share.util.octetstr2str( self.job.device_board.interact( '?tsc' ) ), 2 ** 8 )
    
    return share.trace.Trace( signal_trigger, signal_acquire, tsc = tsc_dec - tsc_nop, data_i = { 'k' : k, 'r' : r, 'c' : c }, data_o = { 'm' : m } )

  def _process_prologue( self ) : 
    t = self.job.device_board.interact( '?id' ).split( ':' )

    if ( len( t ) != 2 ) :
      raise Exception()

    self.driver_type    = t[ 0 ]
    self.driver_version = t[ 1 ]

    if ( self.driver_type    != 'block'               ) :
      raise Exception()
    if ( self.driver_version != share.version.VERSION ) :
      raise Exception()

    self.kernel_sizeof_k = int( self.job.device_board.interact( '?reg k' ), 16 )
    self.kernel_sizeof_r = int( self.job.device_board.interact( '?reg r' ), 16 )
    self.kernel_sizeof_m = int( self.job.device_board.interact( '?reg m' ), 16 )
    self.kernel_sizeof_c = int( self.job.device_board.interact( '?reg c' ), 16 )

    self.job.log.info( 'driver type        = %s', self.driver_type     )
    self.job.log.info( 'driver version     = %s', self.driver_version  )

    self.job.log.info( 'driver sizeof( k ) = %s', self.kernel_sizeof_k )
    self.job.log.info( 'driver sizeof( r ) = %s', self.kernel_sizeof_r )
    self.job.log.info( 'driver sizeof( m ) = %s', self.kernel_sizeof_m )
    self.job.log.info( 'driver sizeof( c ) = %s', self.kernel_sizeof_c )

    self.kernel_k = bytearray( [ random.getrandbits( 8 ) for i in range( self.kernel_sizeof_k ) ] )

  def _process( self ) : 
    if   ( self.driver_spec.get( 'kernel' ) == 'enc' ) :
      trace = self._interact_enc()    
    elif ( self.driver_spec.get( 'kernel' ) == 'dec' ) :
      trace = self._interact_dec()    
  
    return trace

  def _process_epilogue( self ) : 
    pass
