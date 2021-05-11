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

import abc, h5py, os, serial, struct

class BoardAbs( abc.ABC ) :
  def __init__( self, job ) :
    self.job                       = job

    self.board_id                  = self.job.conf.get( 'board_id'   )
    self.board_spec                = self.job.conf.get( 'board_spec' )
    self.board_mode                = self.job.conf.get( 'board_mode' )
    self.board_path                = self.job.conf.get( 'board_path' )

    self.board_uart                = None

    self.driver_version            = None
    self.driver_id                 = None

    self.kernel_id                 = None
    self.kernel_io                 = dict()

  def __str__( self ) :
    return self.board_id

  @abc.abstractmethod
  def get_channel_trigger_range( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def get_channel_trigger_threshold( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def get_channel_acquire_range( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def get_channel_acquire_threshold( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def get_docker_vol ( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def get_docker_env ( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def get_docker_conf( self ) :
    raise NotImplementedError()

  def uart_open( self, port, timeout, mode ) :
    t = mode.split( '/' ) ; mode = {}
  
    if ( len( t      ) != 2 ) :
      raise Exception( 'cannot parse UART mode' )
    if ( len( t[ 1 ] ) != 3 ) :
      raise Exception( 'cannot parse UART mode' )
  
    mode[ 'baudrate' ] = int( t[ 0 ] )
  
    if   ( t[ 1 ][ 0 ] == '5' ) :
      mode[ 'bytesize' ] = serial.FIVEBITS
    elif ( t[ 1 ][ 0 ] == '6' ) :
      mode[ 'bytesize' ] = serial.SIXBITS
    elif ( t[ 1 ][ 0 ] == '7' ) :
      mode[ 'bytesize' ] = serial.SEVENBITS
    elif ( t[ 1 ][ 0 ] == '8' ) :
      mode[ 'bytesize' ] = serial.EIGHTBITS
  
    if   ( t[ 1 ][ 1 ] == 'N' ) :
      mode[ 'parity'   ] = serial.PARITY_NONE
    if   ( t[ 1 ][ 1 ] == 'E' ) :
      mode[ 'parity'   ] = serial.PARITY_EVEN
    if   ( t[ 1 ][ 1 ] == 'O' ) :
      mode[ 'parity'   ] = serial.PARITY_ODD
  
    if   ( t[ 1 ][ 2 ] == '1' ) :
      mode[ 'stopbits' ] = serial.STOPBITS_ONE
    elif ( t[ 1 ][ 2 ] == '2' ) :
      mode[ 'stopbits' ] = serial.STOPBITS_TWO
  
    return serial.Serial( port = port, timeout = timeout, **mode )

  def uart_send( self, x ) :
    self.board_uart.write( ( x + '\x0D' ).encode() )

  def uart_recv( self    ) :
    r = ''

    while( True ):
      t = self.board_uart.read( 1 )

      if( t == '\x0D'.encode() ) :
        break
      else:
        r += ''.join( [ chr( x ) for x in t ] )

    return r

  def hdf5_add_attr( self, fd, ks           ) :
    T = [ ( 'driver_version', str( self.driver_version ), h5py.special_dtype( vlen = str ) ),
          ( 'driver_id',      str( self.driver_id      ), h5py.special_dtype( vlen = str ) ),

          ( 'kernel_id',      str( self.kernel_id      ), h5py.special_dtype( vlen = str ) ),
          ( 'kernel_io',      str( self.kernel_io      ), h5py.special_dtype( vlen = str ) ) ]

    for ( k, v, t ) in T :
      fd.attrs.create( k, v, dtype = t )

  def hdf5_add_data( self, fd, ks, n        ) :
    T = [ ( 'perf/cycle',    ( n, ), '<u8' ),
          ( 'perf/duration', ( n, ), '<f8' ) ]

    for ( k, v, t ) in T :
      if ( k in ks ) :
        fd.create_dataset( k, v, t )

  def hdf5_set_data( self, fd, ks, i, trace ) :
    T = [ ( 'perf/cycle',    lambda trace : trace[ 'perf/cycle'    ] ),
          ( 'perf/duration', lambda trace : trace[ 'perf/duration' ] ) ]

    for ( k, f ) in T :
      if ( k in ks ) :
        fd[ k ][ i ] = f( trace )

  def interact( self, x ) :
    sca3s_be.share.sys.log.debug( '> uart : %s', x )
    self.uart_send( x ) ; t = self.uart_recv()
    sca3s_be.share.sys.log.debug( '< uart : %s', t )

    if   ( t[ 0 ] == '+' ) :
      return t[ 1 : ]
    elif ( t[ 0 ] == '-' ) :
      raise Exception( 'failed board interaction' )
    elif ( t[ 0 ] == '~' ) :
      raise Exception( 'failed board interaction' )
    else :
      raise Exception( 'failed board interaction' )

  def io( self ) :
    fn = os.path.join( self.job.path, 'target', 'build', self.board_id, 'target.io' )

    if ( not os.path.isfile( fn ) ) :
      raise Exception( 'failed to open file' )

    fd = open( fn, 'r' )

    for line in fd.readlines() :
      t = line.split( '=' ) 

      if ( len( t ) != 2 ) :
        continue

      k = t[ 0 ].strip()
      v = t[ 1 ].strip()
        
      self.kernel_io[ k ] = v

    # dump parsed responses

    for ( k, v ) in self.kernel_io.items() :
      self.job.log.info( 'parsed non-interactive I/O response: %s => %s' % ( k, v ) )

    # produce dummy data for each potential output (including TSC as a special case)

    if ( '?kernel_data <' in self.kernel_io ) :
      for id in self.kernel_io[ '?kernel_data <' ].split( ',' ) :
        if ( ( '?data %s' % ( id ) ) in self.kernel_io ) :
          self.kernel_io[ id ] = sca3s_be.share.util.str2octetstr( bytes( [ 0 ] * int( self.kernel_io[ '?data %s' % ( id ) ] ) ) )

    self.kernel_io[ 'tsc' ] = '01:00'

    # convert integer sizes into octet strings

    for ( k, v ) in self.kernel_io.items() :
      if ( k.startswith( '?data' ) ) :
        self.kernel_io[ k ] = sca3s_be.share.util.str2octetstr( struct.pack( '<I', int( v ) ) )

    fd.close()

  @abc.abstractmethod
  def program_hw( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def program_sw( self ) :
    raise NotImplementedError()

  def prepare( self ) :
    t = self.interact( '?kernel_id' ).split( ':' )
  
    if ( len( t ) != 3 ) :
      raise Exception( 'cannot parse kernel identifier' )
  
    self.driver_version = t[ 0 ]
    self.driver_id      = t[ 1 ]
  
    self.kernel_id      = t[ 2 ]
  
    self.job.log.info( '?kernel_id   -> driver version     = %s', self.driver_version )
    self.job.log.info( '?kernel_id   -> driver id          = %s', self.driver_id      )

    self.job.log.info( '?kernel_id   -> kernel id          = %s', self.kernel_id      )
  
    self.kernel_data_i = set( self.job.board.interact( '?kernel_data >' ).split( ',' ) )
    self.kernel_data_o = set( self.job.board.interact( '?kernel_data <' ).split( ',' ) )
  
    self.job.log.info( '?kernel_data -> kernel data  input = %s', self.kernel_data_i  )
    self.job.log.info( '?kernel_data -> kernel data output = %s', self.kernel_data_o  )

  @abc.abstractmethod
  def  open( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def close( self ) :
    raise NotImplementedError()
