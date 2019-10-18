# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend as be
from sca3s import spec    as spec

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import binascii, Crypto.Cipher.AES as AES, h5py, numpy, os, random, re

TVLA_AES = { 16 : { 'k_dev'    : bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF0'                                 ) ),
                    'k_gen'    : bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDE0F0'                                 ) ),
                    'x_fixed'  : bytes( binascii.a2b_hex( 'DA39A3EE5E6B4B0D3255BFEF95601890'                                 ) ),
                    'x_random' : bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) ) },

             24 : { 'k_dev'    : bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF01'                 ) ),
                    'k_gen'    : bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDE0F01'                 ) ),
                    'x_fixed'  : bytes( binascii.a2b_hex( 'DA39A3EE5E6B4B0D3255BFEF95601888'                                 ) ),
                    'x_random' : bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) ) },

             32 : { 'k_dev'    : bytes( binascii.a2b_hex( '0123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDEF012' ) ),
                    'k_gen'    : bytes( binascii.a2b_hex( '123456789ABCDEF123456789ABCDEF023456789ABCDEF013456789ABCDE0F012' ) ),
                    'x_fixed'  : bytes( binascii.a2b_hex( 'DA39A3EE5E6B4B0D3255BFEF95601895'                                 ) ),
                    'x_random' : bytes( binascii.a2b_hex( '00000000000000000000000000000000'                                 ) ) } }

class Block( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.trace_spec    = self.job.conf.get( 'trace-spec' )

    self.trace_content =       self.trace_spec.get( 'content' )
    self.trace_count   =  int( self.trace_spec.get( 'count'   ) )

  def prepare( self ) : 
    if ( self.job.board.driver_id != 'block' ) :
      raise Exception()

    self.kernel_sizeof_k = int( self.job.board.interact( '?reg k' ), 16 )
    self.kernel_sizeof_r = int( self.job.board.interact( '?reg r' ), 16 )
    self.kernel_sizeof_m = int( self.job.board.interact( '?reg m' ), 16 )
    self.kernel_sizeof_c = int( self.job.board.interact( '?reg c' ), 16 )

    self.job.log.info( '?reg k -> kernel sizeof( k ) = %s', self.kernel_sizeof_k )
    self.job.log.info( '?reg r -> kernel sizeof( r ) = %s', self.kernel_sizeof_r )
    self.job.log.info( '?reg m -> kernel sizeof( m ) = %s', self.kernel_sizeof_m )
    self.job.log.info( '?reg c -> kernel sizeof( c ) = %s', self.kernel_sizeof_c )

    if   ( ( self.driver_spec.get( 'policy' ) == 'tvla-fvr-k' ) and ( self.job.board.kernel_id not in [ 'aes' ] ) ): 
      raise Exception()
    elif ( ( self.driver_spec.get( 'policy' ) == 'tvla-fvr-d' ) and ( self.job.board.kernel_id not in [ 'aes' ] ) ): 
      raise Exception()
    elif ( ( self.driver_spec.get( 'policy' ) == 'tvla-svr-d' ) and ( self.job.board.kernel_id not in [ 'aes' ] ) ): 
      raise Exception()
    elif ( ( self.driver_spec.get( 'policy' ) == 'tvla-rvr-d' ) and ( self.job.board.kernel_id not in [ 'aes' ] ) ): 
      raise Exception()

  def _value( self, x ) :
    r = ''
  
    for t in re.split( '({[^}]*})', x ) :
      if ( ( not t.startswith( '{' ) ) or ( not t.endswith( '}' ) ) ) :
        r += t ; continue
    
      ( c, n ) = tuple( t.strip( '{}' ).split( '*' ) )
    
      c = c.strip()
      n = n.strip()
  
      if   ( n == '|k|' ) :
        r += c * ( 2 * self.kernel_sizeof_k )
      elif ( n == '|r|' ) :
        r += c * ( 2 * self.kernel_sizeof_r )
      elif ( n == '|m|' ) :
        r += c * ( 2 * self.kernel_sizeof_m )
      elif ( n == '|c|' ) :
        r += c * ( 2 * self.kernel_sizeof_c )
      else :
        r += c * int( n )

    return bytes( binascii.a2b_hex( ''.join( [ ( '%X' % random.getrandbits( 4 ) ) if ( r[ i ] == '$' ) else ( r[ i ] ) for i in range( len( r ) ) ] ) ) )

  def _acquire_log_inc( self, i, n, message = None ) :
    width = len( str( n ) ) ; message = '' if ( message == None ) else ( ' : ' + message )
    self.job.log.indent_inc( message = 'started  acquiring trace {0:>{width}d} of {1:d} {message:s}'.format( i, n, width = width, message = message  ) )

  def _acquire_log_dec( self, i, n, message = None ) :
    width = len( str( n ) ) ; message = '' if ( message == None ) else ( ' : ' + message )
    self.job.log.indent_dec( message = 'finished acquiring trace {0:>{width}d} of {1:d} {message:s}'.format( i, n, width = width, message = message  ) )

  def _hdf5_get_tvla( self, fd ) :
    n   = 2 * self.trace_count

    lhs = numpy.fromiter( range( 0, int( n / 2 ) ), numpy.int )
    rhs = numpy.fromiter( range( int( n / 2 ), n ), numpy.int )

    if ( 'tvla/lhs' in self.trace_content ) :
      fd[ 'tvla/lhs' ] = lhs
    if ( 'tvla/rhs' in self.trace_content ) :
      fd[ 'tvla/rhs' ] = rhs

    return ( n, lhs, rhs )

  def _hdf5_add_attr( self, fd ) :
    T = [ ( 'driver_version',    self.job.board.driver_version,    h5py.special_dtype( vlen = str ) ),
          ( 'driver_id',         self.job.board.driver_id,         h5py.special_dtype( vlen = str ) ),
          ( 'kernel_id',         self.job.board.kernel_id,         h5py.special_dtype( vlen = str ) ),

          ( 'signal_interval',   self.job.scope.signal_interval,   '<f8'                            ),
          ( 'signal_duration',   self.job.scope.signal_duration,   '<f8'                            ),
    
          ( 'signal_resolution', self.job.scope.signal_resolution, '<u8'                            ),
          ( 'signal_type',       self.job.scope.signal_type,       h5py.special_dtype( vlen = str ) ),
          ( 'signal_length',     self.job.scope.signal_length,     '<u8'                            ),
    
          ( 'kernel_sizeof_k',   self.kernel_sizeof_k,             '<u8'                            ),
          ( 'kernel_sizeof_r',   self.kernel_sizeof_r,             '<u8'                            ),
          ( 'kernel_sizeof_m',   self.kernel_sizeof_m,             '<u8'                            ),
          ( 'kernel_sizeof_c',   self.kernel_sizeof_c,             '<u8'                            ) ]

    for ( k, v, t ) in T :
      fd.attrs.create( k, v, dtype = t )

  def _hdf5_add_data( self, fd, n ) :
    T = [ ( 'trace/trigger',  ( n, self.job.scope.signal_length ), self.job.scope.signal_type                       ),
          ( 'trace/signal',   ( n, self.job.scope.signal_length ), self.job.scope.signal_type                       ),
   
          (  'crop/trigger',  ( n,                              ), h5py.special_dtype( ref = h5py.RegionReference ) ),
          (  'crop/signal',   ( n,                              ), h5py.special_dtype( ref = h5py.RegionReference ) ),
   
          (  'perf/cycle',    ( n,                              ), '<u8'                                            ),
          (  'perf/duration', ( n,                              ), '<f8'                                            ),
   
          ( 'k',              ( n, self.kernel_sizeof_k         ),   'B'                                            ),
          ( 'r',              ( n, self.kernel_sizeof_k         ),   'B'                                            ),
          ( 'm',              ( n, self.kernel_sizeof_k         ),   'B'                                            ),
          ( 'c',              ( n, self.kernel_sizeof_k         ),   'B'                                            ) ]

    for ( k, v, t ) in T :
      if ( k in self.trace_content ) :
        fd.create_dataset( k, v, t )
 
  def _hdf5_set_data( self, fd, trace, i ) :
    T = [ ( 'trace/trigger',  lambda trace : trace[ 'trace/trigger'  ]                                                         ),
          ( 'trace/signal',   lambda trace : trace[ 'trace/signal'   ]                                                         ),

          (  'crop/trigger',  lambda trace :    fd[ 'trace/trigger'  ].regionref[ i, trace[ 'edge/lo' ] : trace[ 'edge/hi' ] ] ),
          (  'crop/signal',   lambda trace :    fd[ 'trace/signal'   ].regionref[ i, trace[ 'edge/lo' ] : trace[ 'edge/hi' ] ] ),

          (  'perf/cycle',    lambda trace : trace[  'perf/cycle'    ]                                                         ),
          (  'perf/duration', lambda trace : trace[  'perf/duration' ]                                                         ),

          ( 'k',              lambda trace : numpy.frombuffer( trace[ 'k' ], dtype = numpy.uint8 )                             ),
          ( 'r',              lambda trace : numpy.frombuffer( trace[ 'r' ], dtype = numpy.uint8 )                             ),
          ( 'm',              lambda trace : numpy.frombuffer( trace[ 'm' ], dtype = numpy.uint8 )                             ),
          ( 'c',              lambda trace : numpy.frombuffer( trace[ 'c' ], dtype = numpy.uint8 )                             ) ]

    for ( k, f ) in T :
      if ( k in self.trace_content ) :
        fd[ k ][ i ] = f( trace )

  # policy: custom

  def _policy_custom( self, fd ) :
    n = self.trace_count ; self._hdf5_add_attr( fd ) ; self._hdf5_add_data( fd, n )

    custom_select = self.driver_spec.get( 'custom-select' )
    custom_value  = self.driver_spec.get( 'custom-value'  )

    k = self._value( custom_value.get( 'k' ) ) if ( custom_select.get( 'k' ) == 'all' ) else None
    m = self._value( custom_value.get( 'm' ) ) if ( custom_select.get( 'm' ) == 'all' ) else None 
    c = self._value( custom_value.get( 'c' ) ) if ( custom_select.get( 'c' ) == 'all' ) else None

    for i in range( n ) :
      if ( custom_select.get( 'k' ) == 'each' ) :
        k = self._value( custom_value.get( 'k' ) )
      if ( custom_select.get( 'm' ) == 'each' ) :
        m = self._value( custom_value.get( 'm' ) )
      if ( custom_select.get( 'c' ) == 'each' ) :
        c = self._value( custom_value.get( 'c' ) )

      self._acquire_log_inc( i, n )
      self._hdf5_set_data( fd, self.acquire( k = k, m = m, c = c ), i )
      self._acquire_log_dec( i, n )

  # Policy: TVLA type 1:  fixed-versus random key.

  def _policy_tvla_fvr_k( self, fd ) :
    raise Exception()

  # Policy: TVLA type 2:  fixed-versus random data.

  def _policy_tvla_fvr_d( self, fd ) :
    ( n, lhs, rhs ) = self._hdf5_get_tvla( fd ) ; self._hdf5_add_attr( fd ) ; self._hdf5_add_data( fd, n )

    k_dev = TVLA_AES[ self.kernel_sizeof_k ][ 'k_dev'    ]
    k_gen = TVLA_AES[ self.kernel_sizeof_k ][ 'k_gen'    ]

    x     = TVLA_AES[ self.kernel_sizeof_k ][ 'x_fixed'  ]

    for i in lhs :
      self._acquire_log_inc( i, n, message = 'LHS (fixed)'  )
      self._hdf5_set_data( fd, self.acquire( k = k_dev, m = x, c = x ), i )
      self._acquire_log_dec( i, n, message = 'LHS (fixed)'  )

    x     = TVLA_AES[ self.kernel_sizeof_k ][ 'x_random' ]

    for i in rhs :
      self._acquire_log_inc( i, n, message = 'RHS (random)' )
      self._hdf5_set_data( fd, self.acquire( k = k_dev, m = x, c = x ), i ) ; x = AES.new( k_gen ).encrypt( x )
      self._acquire_log_dec( i, n, message = 'RHS (random)' )

  # Policy: TVLA type 3:   semi-versus random data.

  def _policy_tvla_svr_d( self, fd ) :
    raise Exception()

  # Policy: TVLA type 4: random-versus random data.

  def _policy_tvla_rvr_d( self, fd ) :
    ( n, lhs, rhs ) = self._hdf5_get_tvla( fd ) ; self._hdf5_add_attr( fd ) ; self._hdf5_add_data( fd, n )

    k_dev = TVLA_AES[ self.kernel_sizeof_k ][ 'k_dev'    ]
    k_gen = TVLA_AES[ self.kernel_sizeof_k ][ 'k_gen'    ]

    x     = TVLA_AES[ self.kernel_sizeof_k ][ 'x_random' ]

    for i in lhs :
      self._acquire_log_inc( i, n, message = 'LHS (random)' )
      self._hdf5_set_data( fd, self.acquire( k = k_dev, m = x, c = x ), i ) ; x = AES.new( k_gen ).encrypt( x )
      self._acquire_log_dec( i, n, message = 'LHS (random)' )

    for i in rhs :
      self._acquire_log_inc( i, n, message = 'RHS (random)' )
      self._hdf5_set_data( fd, self.acquire( k = k_dev, m = x, c = x ), i ) ; x = AES.new( k_gen ).encrypt( x )
      self._acquire_log_dec( i, n, message = 'RHS (random)' )

  # Execute driver process:
  #
  # 1. open     HDF5 file
  # 2. execute selected policy
  # 3. close    HDF5 file
  # 4. compress HDF5 file

  def execute( self ) :
    fd = h5py.File( os.path.join( self.job.path, 'acquire.hdf5' ), 'a' )

    if   ( self.driver_spec.get( 'policy' ) == 'custom'     ) : 
      self._policy_custom( fd )
    elif ( self.driver_spec.get( 'policy' ) == 'tvla-fvr-k' ) : 
      self._policy_tvla_fvr_k( fd )
    elif ( self.driver_spec.get( 'policy' ) == 'tvla-fvr-d' ) : 
      self._policy_tvla_fvr_d( fd )
    elif ( self.driver_spec.get( 'policy' ) == 'tvla-svr-d' ) : 
      self._policy_tvla_svr_d( fd )
    elif ( self.driver_spec.get( 'policy' ) == 'tvla-rvr-d' ) : 
      self._policy_tvla_rvr_d( fd )

    fd.close()

    self.job.run( [ 'gzip', '--quiet', os.path.join( self.job.path, 'acquire.hdf5' ) ] )
