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

from sca3s.backend.acquire import kernel as kernel
from sca3s.backend.acquire import driver as driver

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import numpy

PICOSCOPE_DOWNSAMPLE_MODE_NONE      = 0 
PICOSCOPE_DOWNSAMPLE_MODE_AGGREGATE = 1
PICOSCOPE_DOWNSAMPLE_MODE_DECIMATE  = 2
PICOSCOPE_DOWNSAMPLE_MODE_AVERAGE   = 3

class ScopeType( scope.ScopeAbs ) :
  def __init__( self, job, api ) :
    super().__init__( job )

    self.api                = api

    self.connect_id         = self.scope_spec.get( 'connect_id'         )
    self.connect_timeout    = self.scope_spec.get( 'connect_timeout'    )

    self.channel_trigger_id = self.scope_spec.get( 'channel_trigger_id' )
    self.channel_acquire_id = self.scope_spec.get( 'channel_acquire_id' )
    self.channel_disable_id = self.scope_spec.get( 'channel_disable_id' )

  def calibrate( self, mode = scope.CALIBRATE_MODE_DEFAULT, value = None, resolution = 8, dtype = '<f8' ) :  
    print( resolution )
    print( self._resolutions() )
    resolution = sca3s_be.share.util.closest( self._resolutions(), resolution )
    print( resolution )

    # select configuration
    if   ( mode == scope.CALIBRATE_MODE_DEFAULT   ) :
      interval = self.scope_spec.get( 'acquire_timeout' ) / self._maxSamples( resolution )
      timebase = self._interval2timebase( resolution, interval )
      interval = self._timebase2interval( resolution, timebase ) 
      duration = min( value, interval * self._maxSamples( resolution ) )

    elif ( mode == scope.CALIBRATE_MODE_DURATION  ) :
      interval =     value                                    / self._maxSamples( resolution )
      timebase = self._interval2timebase( resolution, interval )
      interval = self._timebase2interval( resolution, timebase ) 
      duration = min( value, interval * self._maxSamples( resolution ) )

    elif ( mode == scope.CALIBRATE_MODE_INTERVAL  ) :
      interval =     value
      timebase = self._interval2timebase( resolution, interval )
      interval = self._timebase2interval( resolution, timebase ) 
      duration =             interval * self._maxSamples( resolution )

    elif ( mode == scope.CALIBRATE_MODE_FREQUENCY ) :
      interval = 1 / value
      timebase = self._interval2timebase( resolution, interval )
      interval = self._timebase2interval( resolution, timebase ) 
      duration =             interval * self._maxSamples( resolution )

    elif ( mode == scope.CALIBRATE_MODE_AUTO      ) :
      return self._calibrate_auto( resolution = resolution, dtype = dtype )

    # configure segmentation (if supported)
    if ( hasattr( self.scope_object, '_lowLevelMemorySegments'      ) ) :
      self.scope_object.memorySegments( 1 )
    # configure resolution   (if supported)
    if ( hasattr( self.scope_object, '_lowLevelSetDeviceResolution' ) ) :
      self.scope_object.setResolution( resolution )
  
    # configure channels
    self.channel_trigger_range     = self.job.board.get_channel_trigger_range()
    self.channel_trigger_threshold = self.job.board.get_channel_trigger_threshold()
    self.channel_acquire_range     = self.job.board.get_channel_acquire_range()
    self.channel_acquire_threshold = self.job.board.get_channel_acquire_threshold()

    self.scope_object.setChannel( channel = self.channel_trigger_id, enabled = True, coupling = 'DC', VRange = self.channel_trigger_range )
    self.scope_object.setChannel( channel = self.channel_acquire_id, enabled = True, coupling = 'DC', VRange = self.channel_acquire_range )
  
    for channel in self.channel_disable_id :
      self.scope_object.setChannel( channel = channel, enabled = False )

    ( _, samples, samples_max ) = self.scope_object.setSamplingInterval( interval, duration )
  
    # configure signal
    self.signal_resolution = resolution
    self.signal_dtype      = dtype

    self.signal_interval   = interval
    self.signal_duration   = duration
    self.signal_samples    = samples

    return { 'resolution' : self.signal_resolution, 'dtype' : self.signal_dtype, 'interval' : self.signal_interval, 'duration' : self.signal_duration, 'samples' : self.signal_samples }

  def acquire( self, mode = scope.ACQUIRE_MODE_PRIME | scope.ACQUIRE_MODE_FETCH ) :
    if ( mode & scope.ACQUIRE_MODE_PRIME ) :
      # configure trigger
      self.scope_object.setSimpleTrigger( self.channel_trigger_id, threshold_V = self.channel_trigger_threshold, direction = 'Rising', timeout_ms = self.connect_timeout )
    
      # start acquisition
      self.scope_object.runBlock()

    if ( mode & scope.ACQUIRE_MODE_FETCH ) :
      # wait for acquisition to complete  
      self.scope_object.waitReady()
    
      # configure buffers, then transfer
      signal_trigger = self.scope_object.getDataV( channel = self.channel_trigger_id, downSampleMode = self._downSampleMode( PICOSCOPE_DOWNSAMPLE_MODE_NONE ), dtype = numpy.dtype( self.signal_type ).type )
      signal_acquire = self.scope_object.getDataV( channel = self.channel_acquire_id, downSampleMode = self._downSampleMode( PICOSCOPE_DOWNSAMPLE_MODE_NONE ), dtype = numpy.dtype( self.signal_type ).type )

      # stop  acquisition
      self.scope_object.stop()

      return ( signal_trigger, signal_acquire )

  def  open( self ) :
    self.scope_object = self.api( serialNumber = self.connect_id.encode(), connect = True )

    if ( self.scope_object == None ) :
      raise Exception( 'failed to open scope' )

    for t in self.scope_object.getAllUnitInfo().split( '\n' ) :
      self.job.log.info( t )

  def close( self ) :
    if ( self.scope_object != None ) :
      self.scope_object.close()
