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

PICOSCOPE_DOWNSAMPLE_MODE_NONE      = 0 
PICOSCOPE_DOWNSAMPLE_MODE_AGGREGATE = 1
PICOSCOPE_DOWNSAMPLE_MODE_DECIMATE  = 2
PICOSCOPE_DOWNSAMPLE_MODE_AVERAGE   = 3

class PicoScope( scope.ScopeAbs ) :
  def __init__( self, job, api ) :
    super().__init__( job )

    self.api                = api

    self.connect_id         = self.device_spec.get( 'connect-id'         )
    self.connect_timeout    = self.device_spec.get( 'connect-timeout'    )

    self.channel_trigger_id = self.device_spec.get( 'channel-trigger-id' )
    self.channel_acquire_id = self.device_spec.get( 'channel-acquire-id' )
    self.channel_disable_id = self.device_spec.get( 'channel-disable-id' )

  def  open( self ) :
    self.device = self.api( serialNumber = self.connect_id.encode(), connect = True )

    if ( self.device == None ) :
      raise Exception()

    for t in self.device.getAllUnitInfo().split( '\n' ) :
      self.job.log.info( t )

  def close( self ) :
    self.device.close()

  def acquire( self, mode ) :
    if ( self.device == None ) :
      raise Exception()

    if ( mode & scope.ACQUIRE_MODE_PREPARE ) :
      # configure segments   (if supported)
      if ( hasattr( self.device, '_lowLevelMemorySegments'      ) ) :
        self.device.memorySegments( 1 )

      # configure resolution (if supported)
      if ( hasattr( self.device, '_lowLevelSetDeviceResolution' ) ) :
        self.device.setResolution( self.signal_resolution )

      # configure channels
      self.device.setChannel( channel = self.channel_trigger_id, enabled = True, coupling = 'DC', VRange = self.channel_trigger_range )
      self.device.setChannel( channel = self.channel_acquire_id, enabled = True, coupling = 'DC', VRange = self.channel_acquire_range )

      for channel in self.channel_disable_id :
        self.device.setChannel( channel = channel, enabled = False )

      # configure timebase
      ( _, samples, samples_max ) = self.device.setSamplingInterval( self.signal_interval, self.signal_duration )

      # configure trigger
      self.device.setSimpleTrigger( self.channel_trigger_id, threshold_V = self.channel_trigger_threshold, direction = 'Rising', timeout_ms = self.connect_timeout )
    
      # start acquisition
      self.device.runBlock()

    if ( mode & scope.ACQUIRE_MODE_COLLECT ) :
      # wait for acquisition to complete  
      self.device.waitReady()
    
      # configure buffers, then transfer
      signal_trigger = self.device.getDataV( channel = self.channel_trigger_id, downSampleMode = self._downSampleMode( PICOSCOPE_DOWNSAMPLE_MODE_NONE ) )
      signal_acquire = self.device.getDataV( channel = self.channel_acquire_id, downSampleMode = self._downSampleMode( PICOSCOPE_DOWNSAMPLE_MODE_NONE ) )

      # stop  acquisition
      self.device.stop()

      return ( signal_trigger, signal_acquire )

    return None
