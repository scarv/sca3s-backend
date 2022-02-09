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

import abc, h5py, importlib, numexpr, os, serial, struct

class BoardAbs( abc.ABC ) :
  def __init__( self, job ) :
    self.job                       = job

    self.board_id                  = self.job.conf.get( 'board_id'   )
    self.board_spec                = self.job.conf.get( 'board_spec' )
    self.board_mode                = self.job.conf.get( 'board_mode' )
    self.board_path                = self.job.conf.get( 'board_path' )

    self.board_uart                = None

    self.kernel_version            = None

    self.kernel_id                 = None
    self.kernel_id_nameof          = None
    self.kernel_id_modeof          = None

    self.kernel_data_wr_id         =  set()
    self.kernel_data_wr_size       = dict()
    self.kernel_data_wr_type       = dict()

    self.kernel_data_rd_id         =  set()
    self.kernel_data_rd_size       = dict()
    self.kernel_data_rd_type       = dict()

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

  def hdf5_add_attr( self, trace_content, fd              ) :
    fd.attrs.create( 'board/kernel_version',   str( self.kernel_version   ), dtype = h5py.string_dtype() )

    fd.attrs.create( 'board/kernel_id',        str( self.kernel_id        ), dtype = h5py.string_dtype() )
    fd.attrs.create( 'board/kernel_id_nameof', str( self.kernel_id_nameof ), dtype = h5py.string_dtype() )
    fd.attrs.create( 'board/kernel_id_modeof', str( self.kernel_id_modeof ), dtype = h5py.string_dtype() )

    fd.attrs.create( 'board/kernel_io',        str( self.kernel_io        ), dtype = h5py.string_dtype() )

  def hdf5_add_data( self, trace_content, fd, n           ) :
    if ( 'perf/cycle'    in trace_content ) :
      fd.create_dataset( 'perf/cycle',    ( n, ), dtype = '<u8' )
    if ( 'perf/duration' in trace_content ) :
      fd.create_dataset( 'perf/duration', ( n, ), dtype = '<f8' )

  def hdf5_set_data( self, trace_content, fd, n, i, trace ) :
    if ( 'perf/cycle'    in trace_content ) :
      fd[ 'perf/cycle'    ][ i ] = trace[ 'perf/cycle'    ]
    if ( 'perf/duration' in trace_content ) :
      fd[ 'perf/duration' ][ i ] = trace[ 'perf/duration' ]

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

    # produce dummy data for each potential output from kernel

    if ( '<kernel' in self.kernel_io ) :
      for id in self.kernel_io[ '<kernel' ].split( ',' ) :
        if ( ( '|data %s' % ( id ) ) in self.kernel_io ) :
          self.kernel_io[ id ] = sca3s_be.share.util.str2octetstr( bytes( [ 0 ] * int( self.kernel_io[ '|data %s' % ( id ) ] ) ) )

    # convert (evaluated: some sizes might involve simple expressions) integer sizes into octet strings

    for ( k, v ) in self.kernel_io.items() :
      if ( k.startswith( '|data' ) ) :
        self.kernel_io[ k ] = sca3s_be.share.util.int2octetstr( int( numexpr.evaluate( v ) ) )
      if ( k.startswith( '#data' ) ) :
        self.kernel_io[ k ] = sca3s_be.share.util.int2octetstr( int( numexpr.evaluate( v ) ) )

    fd.close()

  @abc.abstractmethod
  def program_hw( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def program_sw( self ) :
    raise NotImplementedError()

  def prepare( self ) :
    t = self.interact( '?kernel' ).split( ':' )
  
    if ( len( t ) != 4 ) :
      raise Exception( 'cannot parse kernel identifier' )
  
    self.kernel_version   = t[ 0 ]

    self.kernel_id        = t[ 1 ]
    self.kernel_id_nameof = t[ 2 ]
    self.kernel_id_modeof = t[ 3 ]
  
    self.job.log.info( '?kernel -> kernel version = %s', self.kernel_version      )

    self.job.log.info( '?kernel -> kernel id      = %s', self.kernel_id           )
    self.job.log.info( '?kernel -> kernel id name = %s', self.kernel_id_nameof    )
    self.job.log.info( '?kernel -> kernel id mode = %s', self.kernel_id_modeof    )

    for id in self.job.board.interact( '>kernel' ).split( ',' ) :
      self.kernel_data_wr_id.add( id )

      self.kernel_data_wr_size[ id ] = sca3s_be.share.util.octetstr2int( self.job.board.interact( '|data %s' % ( id ) ) )
      self.kernel_data_wr_type[ id ] =                              str( self.job.board.interact( '?data %s' % ( id ) ) )

    for id in self.job.board.interact( '<kernel' ).split( ',' ) :
      self.kernel_data_rd_id.add( id )

      self.kernel_data_rd_size[ id ] = sca3s_be.share.util.octetstr2int( self.job.board.interact( '|data %s' % ( id ) ) )
      self.kernel_data_rd_type[ id ] =                              str( self.job.board.interact( '?data %s' % ( id ) ) )

    self.job.log.info( '>kernel -> register id    = %s', self.kernel_data_wr_id   )
    self.job.log.info( '        -> register size  = %s', self.kernel_data_wr_size )
    self.job.log.info( '        -> register type  = %s', self.kernel_data_wr_type )

    self.job.log.info( '<kernel -> register id    = %s', self.kernel_data_rd_id   )
    self.job.log.info( '        -> register size  = %s', self.kernel_data_rd_size )
    self.job.log.info( '        -> register type  = %s', self.kernel_data_rd_type )

  @abc.abstractmethod
  def  open( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def close( self ) :
    raise NotImplementedError()
