# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share  as share

from acquire import board  as board
from acquire import scope  as scope
from acquire import driver as driver

from acquire import repo   as repo
from acquire import depo   as depo

import abc

class DriverAbs( abc.ABC ) :
  def __init__( self, job ) :
    super().__init__()  

    self.job         = job

    self.driver_id   = self.job.conf.get( 'driver-id'   )
    self.driver_spec = self.job.conf.get( 'driver-spec' )

  @abc.abstractmethod
  def prepare( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def acquire( self ) :
    raise NotImplementedError()

  def  execute( self ) :
    trace_spec   = self.job.conf.get( 'trace-spec' )

    trace_count  =  int( trace_spec.get( 'count'    ) )
    trace_format =       trace_spec.get( 'format'   )

    if   ( trace_format == 'pkl' ) :
      trace = share.trace.TracePKL( self.job )
    elif ( trace_format == 'csv' ) :
      trace = share.trace.TraceCSV( self.job )
    elif ( trace_format == 'trs' ) :
      trace = share.trace.TraceTRS( self.job )

    trace.open( trace_count )

    for i in range( trace_count ) :
      self.job.log.indent_inc( message = 'started  acquiring trace {0:>{width}d} of {1:d}'.format( i, trace_count, width = len( str( trace_count ) ) ) )
      trace.update( self.acquire(), i, trace_count )
      self.job.log.indent_dec( message = 'finished acquiring trace {0:>{width}d} of {1:d}'.format( i, trace_count, width = len( str( trace_count ) ) ) )

    trace.close()
