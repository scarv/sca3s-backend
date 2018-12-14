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

import abc

class DriverAbs( abc.ABC ) :
  def __init__( self, job ) :
    super().__init__()  

    self.job         = job

    self.driver_id   = self.job.conf.get( 'driver-id'   )
    self.driver_spec = self.job.conf.get( 'driver-spec' )

  @abc.abstractmethod
  def _process_prologue( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def _process( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def _process_epilogue( self ) :
    raise NotImplementedError()

  def  process_prologue( self ) :
    trace_period_id       = self.job.conf.get( 'trace-period-id'       )
    trace_period_spec     = self.job.conf.get( 'trace-period-spec'     )
    trace_resolution_id   = self.job.conf.get( 'trace-resolution-id'   )
    trace_resolution_spec = self.job.conf.get( 'trace-resolution-spec' )

    self.job.log.indent_inc( message = 'program board' )
    self.job.device_board.program()
    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'open    board' )
    self.job.device_board.open()
    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'open    scope' )

    self.job.device_scope.open()

    self.job.device_scope.channel_trigger_range     = self.job.device_board.get_channel_trigger_range()
    self.job.device_scope.channel_trigger_threshold = self.job.device_board.get_channel_trigger_threshold()
    self.job.device_scope.channel_acquire_range     = self.job.device_board.get_channel_acquire_range()
    self.job.device_scope.channel_acquire_threshold = self.job.device_board.get_channel_acquire_threshold()

    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'configure driver' )

    self._process_prologue()

    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'configure scope'  )

    if ( trace_period_id == 'auto' ) :
      l = share.sys.conf.get( 'kernel', section = 'timeout' )
    
      t = self.job.device_scope.conf( scope.CONF_MODE_DURATION, l )
      self.job.log.info( 'before calibration, configuration = %s', t )

      trace = self._process() ; l = share.util.measure( share.util.MEASURE_MODE_DURATION, trace.signal_trigger, self.job.device_scope.channel_trigger_threshold ) * self.job.device_scope.signal_interval

      t = self.job.device_scope.conf( scope.CONF_MODE_DURATION, l )
      self.job.log.info( 'after  calibration, configuration = %s', t )

    else :
      l = int( trace_period_spec )

      if   ( trace_period_id == 'interval'  ) :
        t = self.job.device_scope.conf( scope.CONF_MODE_INTERVAL,  l )
      elif ( trace_period_id == 'frequency' ) :
        t = self.job.device_scope.conf( scope.CONF_MODE_FREQUENCY, l )
      elif ( trace_period_id == 'duration'  ) :
        t = self.job.device_scope.conf( scope.CONF_MODE_DURATION,  l )

      self.job.log.info(                     'configuration = %s', t )

    self.job.log.indent_dec()

  def  process( self ) :
    trace_count  = self.job.conf.get( 'trace-count'  )
    trace_format = self.job.conf.get( 'trace-format' )

    if   ( trace_format == 'pickle' ) :
      traces = share.trace.TraceSetPickle()
    elif ( trace_format == 'trs'    ) :
      traces = share.trace.TraceSetTRS()

    traces.open()

    for i in range( trace_count ) :
      self.job.log.info( 'started  acquiring trace {0:>{width}d} of {1:d}'.format( i, trace_count, width = len( str( trace_count ) ) ) )
      traces.update( self._process() )
      self.job.log.info( 'finished acquiring trace {0:>{width}d} of {1:d}'.format( i, trace_count, width = len( str( trace_count ) ) ) )

    traces.close()

  def  process_epilogue( self ) :
    self.job.log.indent_inc( message = 'close   board' )
    self.job.device_board.close()
    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'close   scope' )
    self.job.device_scope.close()
    self.job.log.indent_dec()

    self._process_epilogue()
