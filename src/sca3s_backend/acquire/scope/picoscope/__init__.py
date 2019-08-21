# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

import sca3s_backend as be
import sca3s_spec    as spec

from sca3s_backend.acquire import board  as board
from sca3s_backend.acquire import scope  as scope
from sca3s_backend.acquire import driver as driver

from sca3s_backend.acquire import repo   as repo
from sca3s_backend.acquire import depo   as depo

PICOSCOPE_DOWNSAMPLE_MODE_NONE      = 0 
PICOSCOPE_DOWNSAMPLE_MODE_AGGREGATE = 1
PICOSCOPE_DOWNSAMPLE_MODE_DECIMATE  = 2
PICOSCOPE_DOWNSAMPLE_MODE_AVERAGE   = 3

class PicoScope( scope.ScopeAbs ) :
  def __init__( self, job, api ) :
    super().__init__( job )

    self.api                = api

    self.connect_id         = self.scope_spec.get( 'connect-id'         )
    self.connect_timeout    = self.scope_spec.get( 'connect-timeout'    )

    self.channel_trigger_id = self.scope_spec.get( 'channel-trigger-id' )
    self.channel_acquire_id = self.scope_spec.get( 'channel-acquire-id' )
    self.channel_disable_id = self.scope_spec.get( 'channel-disable-id' )

  def  open( self ) :
    self.scope_object = self.api( serialNumber = self.connect_id.encode(), connect = True )

    if ( self.scope_object == None ) :
      raise Exception()

    for t in self.scope_object.getAllUnitInfo().split( '\n' ) :
      self.job.log.info( t )

  def close( self ) :
    self.scope_object.close()

  def acquire( self, mode ) :
    if ( self.scope_object == None ) :
      raise Exception()

    if ( mode & scope.ACQUIRE_MODE_PREPARE ) :
      # configure segments   (if supported)
      if ( hasattr( self.scope_object, '_lowLevelMemorySegments'      ) ) :
        self.scope_object.memorySegments( 1 )

      # configure resolution (if supported)
      if ( hasattr( self.scope_object, '_lowLevelSetDeviceResolution' ) ) :
        self.scope_object.setResolution( self.signal_resolution )

      # configure channels
      self.scope_object.setChannel( channel = self.channel_trigger_id, enabled = True, coupling = 'DC', VRange = self.channel_trigger_range )
      self.scope_object.setChannel( channel = self.channel_acquire_id, enabled = True, coupling = 'DC', VRange = self.channel_acquire_range )

      for channel in self.channel_disable_id :
        self.scope_object.setChannel( channel = channel, enabled = False )

      # configure timebase
      ( _, samples, samples_max ) = self.scope_object.setSamplingInterval( self.signal_interval, self.signal_duration )

      # configure trigger
      self.scope_object.setSimpleTrigger( self.channel_trigger_id, threshold_V = self.channel_trigger_threshold, direction = 'Rising', timeout_ms = self.connect_timeout )
    
      # start acquisition
      self.scope_object.runBlock()

    if ( mode & scope.ACQUIRE_MODE_COLLECT ) :
      # wait for acquisition to complete  
      self.scope_object.waitReady()
    
      # configure buffers, then transfer
      signal_trigger = self.scope_object.getDataV( channel = self.channel_trigger_id, downSampleMode = self._downSampleMode( PICOSCOPE_DOWNSAMPLE_MODE_NONE ) )
      signal_acquire = self.scope_object.getDataV( channel = self.channel_acquire_id, downSampleMode = self._downSampleMode( PICOSCOPE_DOWNSAMPLE_MODE_NONE ) )

      # stop  acquisition
      self.scope_object.stop()

      return ( signal_trigger, signal_acquire )

    return None
