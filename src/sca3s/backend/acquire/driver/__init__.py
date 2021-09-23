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

import abc, h5py, numpy, os

class DriverAbs( abc.ABC ) :
  def __init__( self, job ) :
    self.job           = job

    self.driver_id         = self.job.conf.get( 'driver_id'   )
    self.driver_spec       = self.job.conf.get( 'driver_spec' )

    self.trace_spec        = self.job.conf.get(  'trace_spec' )

    self.trace_content     =       self.trace_spec.get( 'content' )
    self.trace_count_major =  int( self.trace_spec.get( 'count'   ) )
    self.trace_count_minor =  1

    self.policy_id         = self.driver_spec.get( 'policy_id'   )
    self.policy_spec       = self.driver_spec.get( 'policy_spec' )

  def __str__( self ) :
    return self.job.board.kernel_id + '/' + self.job.board.kernel_id_nameof + '(' + self.job.board.kernel_id_modeof + ')'

  # Expand an (abstract, symbolic) value description into a (concrete) sequence of bytes.

  def _expand( self, x ) :
    if   ( type( x ) == tuple ) :
      return tuple( [     self._expand( v )   for      v   in x         ] )
    elif ( type( x ) == dict  ) :
      return dict( [ ( k, self._expand( v ) ) for ( k, v ) in x.items() ] )
    elif ( type( x ) == str   ) :
      return sca3s_be.share.util.value( x, ids = { **self.job.board.kernel_data_wr_size, **self.job.board.kernel_data_rd_size } )

    return x

  # Logging: emit entry re. start  of trace acquisition.

  def _acquire_log_inc( self, n, i, message = None ) :
    width = len( str( n - 1 ) ) ; message = '' if ( message == None ) else ( ': ' + message )
    self.job.log.indent_inc( message = 'started  acquiring trace {0:>{width}d} of {1:d} {message:s}'.format( i, n, width = width, message = message  ) )

  # Logging: emit entry re. finish of trace acquisition.

  def _acquire_log_dec( self, n, i, message = None ) :
    width = len( str( n - 1 ) ) ; message = '' if ( message == None ) else ( ': ' + message )
    self.job.log.indent_dec( message = 'finished acquiring trace {0:>{width}d} of {1:d} {message:s}'.format( i, n, width = width, message = message  ) )

  # Driver policy: TVLA-driven => initialise LHS.

  def _policy_tvla_init_lhs( self, spec,            ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    data        = dict()

    for id in self.job.board.kernel_data_wr_id :
      if ( id == 'esr' ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ] )
      else :
        if  ( tvla_mode == 'fvr_k' ) : #  fixed key,      random data (vs.  random key, random data)
          if ( '$' in self.job.board.kernel_data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ], seed = 0x00 )
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ], seed = 0x01 )
        elif( tvla_mode == 'fvr_d' ) : #  fixed key,      fixed  data (vs.  fixed  key, random data)
          if ( '$' in self.job.board.kernel_data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ], seed = 0x02 ) # LHS = RHS
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ], seed = 0x03 )
        elif( tvla_mode == 'rvr_d' ) : #  fixed key,      random data (vs.  fixed  key, random data)
          if ( '$' in self.job.board.kernel_data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ], seed = 0x04 ) # LHS = RHS
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ], seed = 0x05 )

    return data

  # Driver policy: TVLA-driven => initialise RHS.

  def _policy_tvla_init_rhs( self, spec,            ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    data        = dict()

    for id in self.job.board.kernel_data_wr_id :
      if ( id == 'esr' ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ] )
      else :
        if  ( tvla_mode == 'fvr_k' ) : # (fixed key,      random data  vs.) random key, random data
          if ( '$' in self.job.board.kernel_data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ], seed = 0x10 )
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ], seed = 0x11 )
        elif( tvla_mode == 'fvr_d' ) : # (fixed key,      fixed  data  vs.) fixed  key, random data
          if ( '$' in self.job.board.kernel_data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ], seed = 0x02 ) # LHS = RHS
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ], seed = 0x13 )
        elif( tvla_mode == 'rvr_d' ) : # (fixed key,      random data  vs.) fixed  key, random data
          if ( '$' in self.job.board.kernel_data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ], seed = 0x04 ) # LHS = RHS
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ], seed = 0x15 )

    return data

  # Driver policy: TVLA-driven => step       LHS.

  def _policy_tvla_step_lhs( self, spec, n, i, data ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    for id in self.job.board.kernel_data_wr_id :
      if ( id == 'esr' ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ] )
      else :
        if  ( tvla_mode == 'fvr_k' ) : #  fixed key,      random data (vs.  random key, random data)
          if ( '$' in self.job.board.kernel_data_wr_type[ id ] ) :
            pass
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ] )
        elif( tvla_mode == 'fvr_d' ) : #  fixed key,      fixed  data (vs.  fixed  key, random data)
          if ( '$' in self.job.board.kernel_data_wr_type[ id ] ) :
            pass
          else :
            pass
        elif( tvla_mode == 'rvr_d' ) : #  fixed key,      random data (vs.  fixed  key, random data)
          if ( '$' in self.job.board.kernel_data_wr_type[ id ] ) :
            pass
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ] )

    return data

  # Driver policy: TVLA-driven => step       RHS.

  def _policy_tvla_step_rhs( self, spec, n, i, data ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    for id in self.job.board.kernel_data_wr_id :
      if ( id == 'esr' ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ] )
      else :
        if  ( tvla_mode == 'fvr_k' ) : # (fixed key,      random data  vs.) random key, random data
          if ( '$' in self.job.board.kernel_data_wr_type[ id ] ) :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ] )
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ] )
        elif( tvla_mode == 'fvr_d' ) : # (fixed key,      fixed  data  vs.) fixed  key, random data
          if ( '$' in self.job.board.kernel_data_wr_type[ id ] ) :
            pass
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ] )
        elif( tvla_mode == 'rvr_d' ) : # (fixed key,      random data  vs.) fixed  key, random data
          if ( '$' in self.job.board.kernel_data_wr_type[ id ] ) :
            pass
          else :
            data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ] )

    return data

  # Driver policy: user-driven => initialise.

  def _policy_user_init( self, spec             ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    data        = dict()

    for id in self.job.board.kernel_data_wr_id :
      if ( id == 'esr' ) :
        data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ] )
      else :
        data[ id ] = self._expand( user_value.get( id ) )

    return data

  # Driver policy: user-driven => step.

  def _policy_user_step( self, spec, n, i, data ) :
    user_select = spec.get( 'user_select' )
    user_value  = spec.get( 'user_value'  )

    for id in self.job.board.kernel_data_wr_id :
      if ( id == 'esr' ) :
        data[ id ] = sca3s_be.share.util.randbytes( self.job.board.kernel_data_wr_size[ id ] )
      else :
        data[ id ] = self._expand( user_value.get( id ) ) if ( user_select.get( id ) == 'each' ) else ( data[ id ] )

    return data

  # Driver policy: TVLA-driven => initialise.

  def _policy_tvla_init( self, spec,             mode = 'lhs' ) :
    if   ( mode == 'lhs' ) :
      return self._policy_tvla_init_lhs( spec             )
    elif ( mode == 'rhs' ) :
      return self._policy_tvla_init_rhs( spec             )

    return None

  # Driver policy: TVLA-driven => step.

  def _policy_tvla_step( self, spec, n, i, data, mode = 'lhs' ) :
    if   ( mode == 'lhs' ) :
      return self._policy_tvla_step_lhs( spec, n, i, data )
    elif ( mode == 'rhs' ) :
      return self._policy_tvla_step_rhs( spec, n, i, data )

    return None

  # Support query: user-driven policy.

  def _supports_policy_user( self, spec ) :
    return  True

  # Support query: TVLA-driven policy.

  def _supports_policy_tvla( self, spec ) :
    tvla_mode  = spec.get( 'tvla_mode'  )
    tvla_round = spec.get( 'tvla_round' )

    if  ( tvla_mode == 'fvr_k' ) : #  fixed key,      random data  vs.  random key, random data
      return  True
    elif( tvla_mode == 'fvr_d' ) : #  fixed key,      fixed  data  vs.  fixed  key, random data
      return  True
    elif( tvla_mode == 'svr_d' ) :#   fixed key, semi-fixed  data  vs.  fixed  key, random data
      return False
    elif( tvla_mode == 'rvr_d' ) : #  fixed key,      random data  vs.  fixed  key, random data
      return  True

    return False

  # Support query: verify, i.e., check interactive I/O vs. model.
 
  def _supports_verify( self ) :
    return False

  # Driver policy: user-driven.

  def _policy_user( self, fd ) :
    n   = 1 * self.trace_count_major

    self._hdf5_add_attr( fd ) ; self._hdf5_add_data( fd, n )

    data = self._policy_user_init( self.policy_spec )

    for i in range( n ) :
      self._acquire_log_inc( n, i )
      self._hdf5_set_data( fd, n, i, self.acquire( data ) )
      self._acquire_log_dec( n, i )

      data = self._policy_user_step( self.policy_spec, n, i, data )

  # Driver policy: TVLA-driven.
  #
  # - mode = fvr_k ~>  fixed-versus random  key
  # - mode = fvr_d ~>  fixed-versus random data  
  # - mode = svr_d ~>   semi-versus random data  
  # - mode = rvr_d ~> random-versus random data  

  def _policy_tvla( self, fd ) :
    n   = 2 * self.trace_count_major

    lhs = numpy.fromiter( range( 0, int( n / 2 ) ), numpy.int )
    rhs = numpy.fromiter( range( int( n / 2 ), n ), numpy.int )

    if ( 'tvla/lhs' in self.trace_content ) :
      fd[ 'tvla/lhs' ] = lhs
    if ( 'tvla/rhs' in self.trace_content ) :
      fd[ 'tvla/rhs' ] = rhs

    self._hdf5_add_attr( fd ) ; self._hdf5_add_data( fd, n )

    data = self._policy_tvla_init( self.policy_spec, mode = 'lhs' )

    for i in lhs :
      self._acquire_log_inc( n, i, message = 'lhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )
      self._hdf5_set_data( fd, n, i, self.acquire( data ) )
      self._acquire_log_dec( n, i, message = 'lhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )

      data = self._policy_tvla_step( self.policy_spec, n, i, data, mode = 'lhs' )

    data = self._policy_tvla_init( self.policy_spec, mode = 'rhs' )

    for i in rhs :
      self._acquire_log_inc( n, i, message = 'rhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )
      self._hdf5_set_data( fd, n, i, self.acquire( data ) )
      self._acquire_log_dec( n, i, message = 'rhs of %s' % ( self.policy_spec.get( 'tvla_mode' ) ) )

      data = self._policy_tvla_step( self.policy_spec, n, i, data, mode = 'rhs' )

  # TODO

  def _verify( self, data_wr, data_rd ) :
    return False

  # Post-processing, aka. fixed-function analysis: CI.

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

  # Post-processing, aka. fixed-function analysis: contest.

  def _analyse_contest( self ) :
    self.job.result_response[ 'score' ] = 0

  # HDF5 file manipulation: add attributes

  def _hdf5_add_attr( self, fd              ) :
    spec = list()

    for id in self.job.board.kernel_data_wr_id :
      spec.append( ( 'kernel/sizeof_{0:s}'.format( id ),      self.job.board.kernel_data_wr_size[ id ],   '<u8' ) )
    for id in self.job.board.kernel_data_rd_id :
      spec.append( ( 'kernel/sizeof_{0:s}'.format( id ),      self.job.board.kernel_data_rd_size[ id ],   '<u8' ) )

    sca3s_be.share.sys.log.debug( 'HDF5 => add_addr, spec = %s' % ( str( spec ) ) )

    self.job.board.hdf5_add_attr( self.trace_content, fd              )
    self.job.scope.hdf5_add_attr( self.trace_content, fd              )

    sca3s_be.share.util.hdf5_add_attr( spec, self.trace_content, fd              )

  # HDF5 file manipulation: add data

  def _hdf5_add_data( self, fd, n           ) :
    spec = list()

    for id in self.job.board.kernel_data_wr_id :
      spec.append( (   'data/{0:s}'       .format( id ), ( n, self.job.board.kernel_data_wr_size[ id ] ), 'B'   ) )
      spec.append( (   'data/usedof_{0:s}'.format( id ), ( n,                                          ), '<u8' ) )
    for id in self.job.board.kernel_data_rd_id :
      spec.append( (   'data/{0:s}'       .format( id ), ( n, self.job.board.kernel_data_rd_size[ id ] ), 'B'   ) )
      spec.append( (   'data/usedof_{0:s}'.format( id ), ( n,                                          ), '<u8' ) )

    sca3s_be.share.sys.log.debug( 'HDF5 => add_data, spec = %s' % ( str( spec ) ) )

    self.job.board.hdf5_add_data( self.trace_content, fd, n           )
    self.job.scope.hdf5_add_data( self.trace_content, fd, n           )

    sca3s_be.share.util.hdf5_add_data( spec, self.trace_content, fd, n           )

  # HDF5 file manipulation: set data

  def _hdf5_set_data( self, fd, n, i, trace ) :
    spec = list()

    for id in self.job.board.kernel_data_wr_id :
      spec.append( (   'data/{0:s}'       .format( id ), lambda trace : numpy.frombuffer( trace[ 'data/{0:s}'.format( id ) ], dtype = numpy.uint8 ) ) )
      spec.append( (   'data/usedof_{0:s}'.format( id ), lambda trace :              len( trace[ 'data/{0:s}'.format( id ) ]                      ) ) )
    for id in self.job.board.kernel_data_rd_id :
      spec.append( (   'data/{0:s}'       .format( id ), lambda trace : numpy.frombuffer( trace[ 'data/{0:s}'.format( id ) ], dtype = numpy.uint8 ) ) )
      spec.append( (   'data/usedof_{0:s}'.format( id ), lambda trace :              len( trace[ 'data/{0:s}'.format( id ) ]                      ) ) )

    sca3s_be.share.sys.log.debug( 'HDF5 => set_data, spec = %s' % ( str( spec ) ) )

    self.job.board.hdf5_set_data( self.trace_content, fd, n, i, trace )
    self.job.scope.hdf5_set_data( self.trace_content, fd, n, i, trace )

    sca3s_be.share.util.hdf5_set_data( spec, self.trace_content, fd, n, i, trace )

  # Prepare the driver

  @abc.abstractmethod
  def prepare( self ) :
    raise NotImplementedError()

  # Acquire via driver.

  def acquire( self, data = None ) :
    if ( data == None ) :
      data = dict()

    for id in self.job.board.kernel_data_wr_id :
      if ( not id in data ) :
        data[ id ] = self._expand( '{$*|%s|}' % ( id ) )

      self.job.board.interact( '>data %s %s' % ( id, sca3s_be.share.util.str2octetstr( data[ id ] ).upper() ) )
  
    _                   = self.job.scope.acquire( mode = scope.ACQUIRE_MODE_PRIME )

    self.job.board.interact( '!kernel' + ' ' + '%d' % self.trace_count_minor )
    cycle_enc = sca3s_be.share.util.octetstr2int( self.job.board.interact( '<data fcc' ) )

    ( trigger, signal ) = self.job.scope.acquire( mode = scope.ACQUIRE_MODE_FETCH )

    self.job.board.interact( '!nop'    + ' ' + '%d' % self.trace_count_minor )
    cycle_nop = sca3s_be.share.util.octetstr2int( self.job.board.interact( '<data fcc' ) )

    edge_pos = sca3s_be.share.util.measure( sca3s_be.share.util.MEASURE_MODE_TRIGGER_POS, trigger, self.job.scope.channel_trigger_threshold )
    edge_neg = sca3s_be.share.util.measure( sca3s_be.share.util.MEASURE_MODE_TRIGGER_NEG, trigger, self.job.scope.channel_trigger_threshold )

    duration = float( edge_neg - edge_pos ) * self.job.scope.signal_interval
  
    for id in self.job.board.kernel_data_rd_id :
      data[ id ] = sca3s_be.share.util.octetstr2str( self.job.board.interact( '<data %s' % ( id ) ) )

    data_wr = { id : data[ id ] for id in self.job.board.kernel_data_wr_id }
    data_rd = { id : data[ id ] for id in self.job.board.kernel_data_rd_id }

    self.job.log.info( 'acquire: data_wr => %s' % str( data_wr ) )
    self.job.log.info( 'acquire: data_rd => %s' % str( data_rd ) )

    if ( ( self.job.board.board_mode == 'interactive' ) and self._supports_verify() ) :
      if ( not self._verify( data_wr, data_rd ) ) :
        raise Exception( 'failed I/O verification: interactive I/O != model' )

    trace = { 'trace/trigger' : trigger, 'trace/signal' : signal, 'edge/pos' : edge_pos, 'edge/neg' : edge_neg, 'perf/cycle' : cycle_enc - cycle_nop, 'perf/duration' : duration }

    trace.update( { 'data/%s'        % ( id ) :      data_wr[ id ]   for id in self.job.board.kernel_data_wr_id } )
    trace.update( { 'data/usedof_%s' % ( id ) : len( data_wr[ id ] ) for id in self.job.board.kernel_data_wr_id } )
    trace.update( { 'data/%s'        % ( id ) :      data_rd[ id ]   for id in self.job.board.kernel_data_rd_id } )
    trace.update( { 'data/usedof_%s' % ( id ) : len( data_rd[ id ] ) for id in self.job.board.kernel_data_rd_id } )

    self.job.log.debug( 'acquire => trace= %s' % ( str( trace ) ) )

    return trace

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

    self.job.log.indent_inc( message = 'dump acquisition summary' )
    fd.visititems( lambda k, v : self.job.log.info( str( k ) ) )
    self.job.log.indent_dec()

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
