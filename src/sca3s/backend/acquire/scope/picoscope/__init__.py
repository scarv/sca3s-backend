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

import numpy

PICOSCOPE_DOWNSAMPLE_MODE_NONE      = 0 
PICOSCOPE_DOWNSAMPLE_MODE_AGGREGATE = 1
PICOSCOPE_DOWNSAMPLE_MODE_DECIMATE  = 2
PICOSCOPE_DOWNSAMPLE_MODE_AVERAGE   = 3

class ScopeType( scope.ScopeAbs ) :
  def __init__( self, job, api ) :
    super().__init__( job )

    self.api                     = api

    self.unit_id                 = self.scope_spec.get(            'unit_id'      )
    self.unit_timeout            = self.scope_spec.get(            'unit_timeout' )

    self.channel_trigger_timeout = self.scope_spec.get( 'channel_trigger_timeout' )

    self.channel_trigger_id      = self.scope_spec.get( 'channel_trigger_id'      )
    self.channel_acquire_id      = self.scope_spec.get( 'channel_acquire_id'      )
    self.channel_disable_id      = self.scope_spec.get( 'channel_disable_id'      )

  def conf_derive( self, mode, dtype = None, resolution = None, interval = None, duration = None ) :
    if   ( mode == scope.CONF_DERIVE_RESOLUTION ) :
      return sca3s_be.share.util.closest( resolution, self._resolutions() )

    elif ( mode == scope.CONF_DERIVE_INTERVAL   ) :
      interval =                            1 / self._maxSamples( resolution )
      timebase = self._interval2timebase( resolution, interval )
      interval = self._timebase2interval( resolution, timebase ) 

      return interval

    elif ( mode == scope.CONF_DERIVE_DURATION   ) :
      return self.calibrate( dtype = dtype, resolution = resolution )

  def conf_select( self, mode, dtype = None, resolution = None, interval = None, duration = None ) :
    if   ( mode == scope.CONF_SELECT_DEFAULT    ) :
      interval = self.channel_trigger_timeout / self._maxSamples( resolution )
      timebase = self._interval2timebase( resolution, interval )
      interval = self._timebase2interval( resolution, timebase ) 

      duration =                     interval * self._maxSamples( resolution )  

    elif ( mode == scope.CONF_SELECT_DERIVED    ) :
      pass

    if ( hasattr( self.scope_unit, '_lowLevelMemorySegments'      ) ) :
      self.scope_unit.memorySegments( 1 )
    if ( hasattr( self.scope_unit, '_lowLevelSetDeviceResolution' ) ) :
      self.scope_unit.setResolution( str( resolution ) )
  
    self.channel_trigger_range     = self.job.board.get_channel_trigger_range()
    self.channel_trigger_threshold = self.job.board.get_channel_trigger_threshold()
    self.channel_acquire_range     = self.job.board.get_channel_acquire_range()
    self.channel_acquire_threshold = self.job.board.get_channel_acquire_threshold()

    self.scope_unit.setChannel( channel = self.channel_trigger_id, enabled = True, coupling = 'DC', VRange = self.channel_trigger_range )
    self.scope_unit.setChannel( channel = self.channel_acquire_id, enabled = True, coupling = 'DC', VRange = self.channel_acquire_range )
  
    for channel in self.channel_disable_id :
      self.scope_unit.setChannel( channel = channel, enabled = False )

    ( _, samples, samples_max ) = self.scope_unit.setSamplingInterval( interval, duration )
  
    self.signal_dtype      = dtype
    self.signal_resolution = resolution

    self.signal_interval   = interval
    self.signal_duration   = duration

    self.signal_samples    = samples

    return { 'dtype' : self.signal_dtype, 'resolution' : self.signal_resolution, 'interval' : self.signal_interval, 'duration' : self.signal_duration, 'samples' : self.signal_samples }

  def acquire( self, mode = scope.ACQUIRE_MODE_PRIME | scope.ACQUIRE_MODE_FETCH ) :
    if ( mode & scope.ACQUIRE_MODE_PRIME ) :
      # configure trigger
      self.scope_unit.setSimpleTrigger( self.channel_trigger_id, threshold_V = self.channel_trigger_threshold, direction = 'Rising', timeout_ms = int( self.channel_trigger_timeout * 1.0e3 ) )
    
      # start acquisition
      self.scope_unit.runBlock()

    if ( mode & scope.ACQUIRE_MODE_FETCH ) :
      # wait for acquisition to complete  
      self.scope_unit.waitReady()
    
      # configure buffers, then transfer
      signal_trigger = self.scope_unit.getDataV( channel = self.channel_trigger_id, downSampleMode = self._downSampleMode( PICOSCOPE_DOWNSAMPLE_MODE_NONE ), dtype = numpy.dtype( self.signal_dtype ).type )
      signal_acquire = self.scope_unit.getDataV( channel = self.channel_acquire_id, downSampleMode = self._downSampleMode( PICOSCOPE_DOWNSAMPLE_MODE_NONE ), dtype = numpy.dtype( self.signal_dtype ).type )

      # stop  acquisition
      self.scope_unit.stop()

      return ( signal_trigger, signal_acquire )

  def  open( self ) :
    self.scope_unit = self.api( serialNumber = self.unit_id.encode(), connect = True )

    if ( self.scope_unit == None ) :
      raise Exception( 'failed to open scope' )

    for t in self.scope_unit.getAllUnitInfo().split( '\n' ) :
      self.job.log.info( t )

  def close( self ) :
    if ( self.scope_unit != None ) :
      self.scope_unit.close()
