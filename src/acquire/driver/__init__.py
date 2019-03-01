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
    trace_spec            = self.job.conf.get( 'trace-spec' )

    trace_period_id       = trace_spec.get( 'period-id'       )
    trace_period_spec     = trace_spec.get( 'period-spec'     )
    trace_resolution_id   = trace_spec.get( 'resolution-id'   )
    trace_resolution_spec = trace_spec.get( 'resolution-spec' )

    self.job.log.indent_inc( message = 'open  board' )

    self.job.device_board.program()
    self.job.device_board.open()

    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'open  scope' )

    self.job.device_scope.open()

    self.job.device_scope.channel_trigger_range     = self.job.device_board.get_channel_trigger_range()
    self.job.device_scope.channel_trigger_threshold = self.job.device_board.get_channel_trigger_threshold()
    self.job.device_scope.channel_acquire_range     = self.job.device_board.get_channel_acquire_range()
    self.job.device_scope.channel_acquire_threshold = self.job.device_board.get_channel_acquire_threshold()

    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'configure driver' )
    self._process_prologue()
    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'calibrate scope'  )

    if ( trace_period_id == 'auto' ) :
      l = share.sys.conf.get( 'timeout', section = 'job' )
    
      t = self.job.device_scope.conf( scope.CONF_MODE_DURATION, 1 * l )

      self.job.log.info( 'before calibration, configuration = %s', t )

      trace = self._process() ; l = share.util.measure( share.util.MEASURE_MODE_DURATION, trace.signal_trigger, self.job.device_scope.channel_trigger_threshold ) * self.job.device_scope.signal_interval
      t = self.job.device_scope.conf( scope.CONF_MODE_DURATION, 2 * l )

      trace = self._process() ; l = share.util.measure( share.util.MEASURE_MODE_DURATION, trace.signal_trigger, self.job.device_scope.channel_trigger_threshold ) * self.job.device_scope.signal_interval
      t = self.job.device_scope.conf( scope.CONF_MODE_DURATION, 1 * l )

      self.job.log.info( 'after  calibration, configuration = %s', t )

    else :
      l = trace_period_spec

      if   ( trace_period_id == 'interval'  ) :
        t = self.job.device_scope.conf( scope.CONF_MODE_INTERVAL,  l )
      elif ( trace_period_id == 'frequency' ) :
        t = self.job.device_scope.conf( scope.CONF_MODE_FREQUENCY, l )
      elif ( trace_period_id == 'duration'  ) :
        t = self.job.device_scope.conf( scope.CONF_MODE_DURATION,  l )

      self.job.log.info(                     'configuration = %s', t )

    self.job.log.indent_dec()

  def  process( self ) :
    trace_spec            = self.job.conf.get( 'trace-spec' )

    trace_count           =  int( trace_spec.get( 'count'  ) )
    trace_format          =       trace_spec.get( 'format' )
    trace_crop            = bool( trace_spec.get( 'crop'   ) )

    if   ( trace_format == 'pickle' ) :
      traces = share.trace.TraceSetPickle()
    elif ( trace_format == 'trs'    ) :
      traces = share.trace.TraceSetTRS()

    traces.open()

    for i in range( trace_count ) :
      self.job.log.indent_inc( message = 'started  acquiring trace {0:>{width}d} of {1:d}'.format( i, trace_count, width = len( str( trace_count ) ) ) )

      trace = self._process()

      l = share.util.measure( share.util.MEASURE_MODE_DURATION, trace.signal_trigger, self.job.device_scope.channel_trigger_threshold )

      self.job.log.info( 'measure via TSC    => {0:d}'.format( trace.tsc ) )
      self.job.log.info( 'measure via signal => {0:g}'.format( l         ) )

      if ( trace_crop ) :
        edge_pos = share.util.measure( share.util.MEASURE_MODE_TRIGGER_POS, trace.signal_trigger, self.job.device_scope.channel_trigger_threshold )
        edge_neg = share.util.measure( share.util.MEASURE_MODE_TRIGGER_NEG, trace.signal_trigger, self.job.device_scope.channel_trigger_threshold )

        self.job.log.info( 'crop wrt. +ve trigger edge @ {0:d}'.format( edge_pos ) )
        self.job.log.info( 'crop wrt. -ve trigger edge @ {0:d}'.format( edge_neg ) )

        trace.signal_trigger = trace.signal_trigger[ edge_pos : edge_neg ]
        trace.signal_acquire = trace.signal_acquire[ edge_pos : edge_neg ]

      traces.update( trace )

      self.job.log.indent_dec( message = 'finished acquiring trace {0:>{width}d} of {1:d}'.format( i, trace_count, width = len( str( trace_count ) ) ) )

    traces.close()

  def  process_epilogue( self ) :
    self.job.log.indent_inc( message = 'close board' )
    self.job.device_board.close()
    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'close scope' )
    self.job.device_scope.close()
    self.job.log.indent_dec()

    self._process_epilogue()
