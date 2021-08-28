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
from sca3s.backend.acquire import kernel as kernel

from sca3s.backend.acquire import repo   as repo
from sca3s.backend.acquire import depo   as depo

import abc, h5py, numpy, os

class DriverAbs( abc.ABC ) :
  def __init__( self, job ) :
    self.job           = job

    self.driver_id     = self.job.conf.get( 'driver_id'   )
    self.driver_spec   = self.job.conf.get( 'driver_spec' )

    self.trace_spec    = self.job.conf.get( 'trace_spec' )

    self.trace_content =       self.trace_spec.get( 'content' )
    self.trace_count   =  int( self.trace_spec.get( 'count'   ) )

    self.policy_id     = self.driver_spec.get( 'policy_id'   )
    self.policy_spec   = self.driver_spec.get( 'policy_spec' )

  def __str__( self ) :
    return self.driver_id + ' ' + '(' + self.job.board.kernel_id + ')'

  # Measure the duration of trigger period (wrt. current scope configuration).

  def _measure( self, trigger ) :
    edge_pos = sca3s_be.share.util.measure( sca3s_be.share.util.MEASURE_MODE_TRIGGER_POS, trigger, self.job.scope.channel_trigger_threshold )
    edge_neg = sca3s_be.share.util.measure( sca3s_be.share.util.MEASURE_MODE_TRIGGER_NEG, trigger, self.job.scope.channel_trigger_threshold )
      
    return ( edge_pos, edge_neg, float( edge_neg - edge_pos ) * self.job.scope.signal_interval )

  # Logging: emit entry re. start  of trace acquisition.

  def _acquire_log_inc( self, n, i, message = None ) :
    width = len( str( n - 1 ) ) ; message = '' if ( message == None ) else ( ': ' + message )
    self.job.log.indent_inc( message = 'started  acquiring trace {0:>{width}d} of {1:d} {message:s}'.format( i, n, width = width, message = message  ) )

  # Logging: emit entry re. finish of trace acquisition.

  def _acquire_log_dec( self, n, i, message = None ) :
    width = len( str( n - 1 ) ) ; message = '' if ( message == None ) else ( ': ' + message )
    self.job.log.indent_dec( message = 'finished acquiring trace {0:>{width}d} of {1:d} {message:s}'.format( i, n, width = width, message = message  ) )

  # Driver policy: user-driven

  def _policy_user( self, fd ) :
    n   = 1 * self.trace_count

    self.hdf5_add_attr( fd ) ; self.hdf5_add_data( fd, n )

    data = self.job.board.kernel.policy_user_init( self.policy_spec )

    for i in range( n ) :
      self._acquire_log_inc( n, i )
      self.hdf5_set_data( fd, n, i, self.acquire( data ) )
      self._acquire_log_dec( n, i )

      data = self.job.board.kernel.policy_user_step( self.policy_spec, n, i, data )

  # Driver policy: TVLA-driven
  #
  # - mode = fvr_k ~>  fixed-versus random  key
  # - mode = fvr_d ~>  fixed-versus random data  
  # - mode = svr_d ~>   semi-versus random data  
  # - mode = rvr_d ~> random-versus random data  

  def _policy_tvla( self, fd ) :
    n   = 2 * self.trace_count

    lhs = numpy.fromiter( range( 0, int( n / 2 ) ), numpy.int )
    rhs = numpy.fromiter( range( int( n / 2 ), n ), numpy.int )

    if ( 'tvla/lhs' in self.trace_content ) :
      fd[ 'tvla/lhs' ] = lhs
    if ( 'tvla/rhs' in self.trace_content ) :
      fd[ 'tvla/rhs' ] = rhs

    self.hdf5_add_attr( fd ) ; self.hdf5_add_data( fd, n )

    data = self.job.board.kernel.policy_tvla_init( self.policy_spec, mode = 'lhs' )

    for i in lhs :
      self._acquire_log_inc( n, i, message = 'lhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )
      self.hdf5_set_data( fd, n, i, self.acquire( data ) )
      self._acquire_log_dec( n, i, message = 'lhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )

      data = self.job.board.kernel.policy_tvla_step( self.policy_spec, n, i, data, mode = 'lhs' )

    data = self.job.board.kernel.policy_tvla_init( self.policy_spec, mode = 'rhs' )

    for i in rhs :
      self._acquire_log_inc( n, i, message = 'rhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )
      self.hdf5_set_data( fd, n, i, self.acquire( data ) )
      self._acquire_log_dec( n, i, message = 'rhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )

      data = self.job.board.kernel.policy_tvla_step( self.policy_spec, n, i, data, mode = 'rhs' )

  # Post-processing, aka. fixed-function analysis: CI 

  def _analyse_ci( self ) :    
    doc = sca3s_be.share.report.Report( self.job )

    self.job.log.indent_inc( message = 'generate report preamble' )
    doc.emit_preamble()
    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'generate report prologue' )
    doc.emit_prologue()
    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'generate report content: calibration report' )
    doc.emit_section_calibrate()
    self.job.log.indent_dec()
    self.job.log.indent_inc( message = 'generate report content: latency     report' )
    doc.emit_section_latency()
    self.job.log.indent_dec()
    self.job.log.indent_inc( message = 'generate report content: leakage     report' )
    doc.emit_section_leakage()
    self.job.log.indent_dec()

    self.job.log.indent_inc( message = 'generate report epilogue' )
    doc.emit_epilogue()
    self.job.log.indent_dec()
  
    self.job.log.indent_inc( message = 'compile  report'          )
    doc.compile( os.path.join( self.job.path, 'acquire.pdf' ) )
    self.job.log.indent_dec()
    
    self.job.result_transfer[ 'acquire.pdf' ] = { 'ContentType': 'application/pdf', 'CacheControl': 'no-cache, max-age=0', 'ACL': 'public-read' }

  # Post-processing, aka. fixed-function analysis: contest

  def _analyse_contest( self ) :
    self.job.result_response[ 'score' ] = 0

  # HDF5 file manipulation: add attributes

  @abc.abstractmethod
  def hdf5_add_attr( self, fd              ) :
    raise NotImplementedError()

  # HDF5 file manipulation: add data

  @abc.abstractmethod
  def hdf5_add_data( self, fd, n           ) :
    raise NotImplementedError()

  # HDF5 file manipulation: set data

  @abc.abstractmethod
  def hdf5_set_data( self, fd, n, i, trace ) :
    raise NotImplementedError()

  # Acquire via driver

  def acquire( self, data = None ) :
    if ( data == None ) :
      data = dict()

    for id in self.job.board.kernel.data_wr_id :
      if ( not id in data ) :
        data[ id ] = self.job.board.kernel.expand( '{$*|%s|}' % ( id ) )

      self.job.board.interact( '>data %s %s' % ( id, sca3s_be.share.util.str2octetstr( data[ id ] ).upper() ) )
  
    _                   = self.job.scope.acquire( mode = scope.ACQUIRE_MODE_PRIME )

    self.job.board.interact( '!kernel_prologue' )
 
    self.job.board.interact( '!kernel'          )
    cycle_enc = sca3s_be.share.util.octetstr2int( self.job.board.interact( '<data fcc' ) )
    self.job.board.interact( '!kernel_nop' )
    cycle_nop = sca3s_be.share.util.octetstr2int( self.job.board.interact( '<data fcc' ) )

    self.job.board.interact( '!kernel_epilogue' )
  
    ( trigger, signal ) = self.job.scope.acquire( mode = scope.ACQUIRE_MODE_FETCH )
    ( edge_pos, edge_neg, duration ) = self._measure( trigger )
  
    for id in self.job.board.kernel.data_rd_id :
      data[ id ] = sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data %s' % ( id ) ) )

    data_wr = { id : data[ id ] for id in self.job.board.kernel.data_wr_id }
    data_rd = { id : data[ id ] for id in self.job.board.kernel.data_rd_id }

    self.job.log.info( 'acquire: data_wr => %s' % str( data_wr ) )
    self.job.log.info( 'acquire: data_rd => %s' % str( data_rd ) )

    if ( ( self.job.board.board_mode == 'interactive' ) and self.job.board.kernel.supports_model() ) :
      if ( self.job.board.kernel.model( data_wr, data_rd ) ) :
        raise Exception( 'failed I/O verification: interactive I/O != model' )

    trace = { 'trace/trigger' : trigger, 'trace/signal' : signal, 'edge/pos' : edge_pos, 'edge/neg' : edge_neg, 'perf/cycle' : cycle_enc - cycle_nop, 'perf/duration' : duration }

    trace.update( { 'data/%s'        % ( id ) :      data_wr[ id ]   for id in self.job.board.kernel.data_wr_id } )
    trace.update( { 'data/usedof_%s' % ( id ) : len( data_wr[ id ] ) for id in self.job.board.kernel.data_wr_id } )
    trace.update( { 'data/%s'        % ( id ) :      data_rd[ id ]   for id in self.job.board.kernel.data_rd_id } )
    trace.update( { 'data/usedof_%s' % ( id ) : len( data_rd[ id ] ) for id in self.job.board.kernel.data_rd_id } )

    return trace

  # Prepare the driver

  @abc.abstractmethod
  def prepare( self ) :
    raise NotImplementedError()

  # Execute the driver prologue

  def execute_prologue( self ) :
    pass

  # Execute the driver

  def execute( self ) :
    fd = h5py.File( os.path.join( self.job.path, 'acquire.hdf5' ), 'a' )

    if   ( self.policy_id == 'user' ) : 
      self._policy_user( fd )
    elif ( self.policy_id == 'tvla' ) : 
      self._policy_tvla( fd )

    fd.close()

  # Execute the driver epilogue

  def execute_epilogue( self ) :
    if   ( self.job.type == 'user'    ) :
      pass
    elif ( self.job.type == 'ci'      ) :
      self._analyse_ci()
    elif ( self.job.type == 'contest' ) :
      self._analyse_contest()

    self.job.exec_native( [ 'gzip', '--quiet', os.path.join( self.job.path, 'acquire.hdf5' ) ] )
