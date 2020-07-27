# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

from sca3s.backend.acquire import board  as board
from sca3s.backend.acquire import scope  as scope
from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

from sca3s.backend.acquire import hybrid as hybrid

import os, trsfile

class HybridImp( hybrid.HybridAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

  # board

  def get_channel_trigger_range( self ) :
    return 1.0E-0

  def get_channel_trigger_threshold( self ) :
    return 1.0E-0

  def get_channel_acquire_range( self ) :
    return 1.0E-0

  def get_channel_acquire_threshold( self ) :
    return None

  def get_docker_vol ( self ) :
    return {}

  def get_docker_env ( self ) :
    return {}

  def get_docker_conf( self ) :
    t = [ '-DDRIVER_NONINTERACTIVE' ]

    if ( '?kernel_data >' in self.kernel_io ) :
      for id in self.kernel_io[ '?kernel_data <' ].split( ',' ) :
        t.append( '-DKERNEL_INITOF_%s="%s"' % ( id.upper(), ','.join( [ '0x%02X' % ( x ) for x in sca3s_be.share.util.octetstr2str( self.interact( '<data %s' % ( id ) ) ) ] ) ) )

    return t

  def uart_send( self, x ) :
    pass

  def uart_recv( self    ) :
    pass

  def  interact( self, x ) :
    def get_cached( k    ) :
      if( not k in self.kernel_io ) :
        raise Exception( 'unable to respond to non-interactive I/O request: %s' % ( k ) )

      v = self.kernel_io[ k ] ; return v

    def set_cached( k, v ) :
      self.kernel_io[ k ] = v ; return v

    if   ( x.startswith( '?data'            ) ) :
      return get_cached( x              )

    elif ( x.startswith( '<data'            ) ) :
      x = x.split( ' ' )
      return get_cached( x[ 1 ]         )
    elif ( x.startswith( '>data'            ) ) :
      x = x.split( ' ' ) ; 
      return set_cached( x[ 1 ], x[ 2 ] )

    elif ( x.startswith( '?kernel_id'       ) ) :
      return get_cached( x              )
    elif ( x.startswith( '?kernel_data'     ) ) :
      return get_cached( x              )

    elif ( x.startswith( '!kernel_prologue' ) ) :
      pass
    elif ( x.startswith( '!kernel_epiloge'  ) ) :
      pass
    elif ( x.startswith( '!kernel'          ) ) :
      self.job.exec_docker(    'clean-harness', quiet = True )
      self.job.exec_docker(    'build-harness', quiet = True )

      self.job.exec_docker( 'simulate-harness', quiet = True )

    elif ( x.startswith( '!nop'             ) ) :
      pass

    return ''

  def   program( self ) :
    pass

  # scope

  def calibrate( self, mode = scope.CALIBRATE_MODE_DEFAULT, value = None, resolution = 8, dtype = '<f8' ) :  
    def mode_duration( x ) :
      interval = 1
      duration = x

      return ( interval, duration )

    if   ( mode == scope.CALIBRATE_MODE_DEFAULT   ) :
      ( interval, duration ) = mode_duration ( self.scope_spec.get( 'acquire_timeout' ) )
    elif ( mode == scope.CALIBRATE_MODE_DURATION  ) :
      ( interval, duration ) = mode_duration ( value                                    )
    elif ( mode == scope.CALIBRATE_MODE_INTERVAL  ) :
      raise Exception( 'unsupported calibration mode' )
    elif ( mode == scope.CALIBRATE_MODE_FREQUENCY ) :
      raise Exception( 'unsupported calibration mode' )

    samples = duration

    # configure channel
    self.channel_trigger_range     = self.get_channel_trigger_range()
    self.channel_trigger_threshold = self.get_channel_trigger_threshold()
    self.channel_acquire_range     = self.get_channel_acquire_range()
    self.channel_acquire_threshold = self.get_channel_acquire_threshold()

    # configure signal
    self.signal_resolution = resolution
    self.signal_dtype      = dtype

    self.signal_interval   = interval
    self.signal_duration   = duration
    self.signal_samples    = samples

    return { 'resolution' : self.signal_resolution, 'dtype' : self.signal_dtype, 'interval' : self.signal_interval, 'duration' : self.signal_duration, 'samples' : self.signal_samples }

  def   acquire( self,    mode = scope.ACQUIRE_MODE_PRIME | scope.ACQUIRE_MODE_FETCH ) :
    if ( mode & scope.ACQUIRE_MODE_PRIME ) :
      pass

    if ( mode & scope.ACQUIRE_MODE_FETCH ) :
      fn = os.path.join( self.job.path, 'target', 'build', self.board_id, 'target.trs' )

      if ( not os.path.isfile( fn ) ) :
        raise Exception( 'failed to open %s' % ( fn ) )

      fd = trsfile.open( fn, 'r' ) ; 

      signal_trigger = f( [ self.get_channel_trigger_threshold() ] * len( fd[ 0 ] ) )
      signal_acquire = f(                                                 fd[ 0 ]   )

      fd.close()

      return ( signal_trigger, signal_acquire )

  # hybrid

  def      open( self ) :
    pass

  def     close( self ) :
    pass
