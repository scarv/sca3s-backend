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

import binascii, h5py, importlib, numpy, os

class DriverImp( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )

    self.trace_spec    = self.job.conf.get( 'trace_spec' )

    self.trace_content =       self.trace_spec.get( 'content' )
    self.trace_count   =  int( self.trace_spec.get( 'count'   ) )

    self.policy_id     = self.driver_spec.get( 'policy_id'   )
    self.policy_spec   = self.driver_spec.get( 'policy_spec' )

  def __str__( self ) :
    return self.driver_id

  # HDF5 file manipulation: add attributes
   
  def _hdf5_add_attr( self, fd, ks           ) :
    T = [ ( 'kernel_sizeof_x', self.kernel.sizeof_k, '<u8' ),
          ( 'kernel_sizeof_r', self.kernel.sizeof_c, '<u8' ) ]
    
    self.job.board.hdf5_add_attr( fd, ks           )
    self.job.scope.hdf5_add_attr( fd, ks           )

    for ( k, v, t ) in T :
      fd.attrs.create( k, v, dtype = t )

  # HDF5 file manipulation: add data

  def _hdf5_add_data( self, fd, ks, n        ) :
    T = [ ( 'x', ( n, self.kernel.sizeof_r ), 'B' ),
          ( 'r', ( n, self.kernel.sizeof_c ), 'B' ) ]

    self.job.board.hdf5_add_data( fd, ks, n        )
    self.job.scope.hdf5_add_data( fd, ks, n        )

    for ( k, v, t ) in T :
      if ( k in ks ) :
        fd.create_dataset( k, v, t )
 
  # HDF5 file manipulation: set data

  def _hdf5_set_data( self, fd, ks, i, trace ) :
    T = [ ( 'x', lambda trace : numpy.frombuffer( trace[ 'x' ], dtype = numpy.uint8 ) ),
          ( 'r', lambda trace : numpy.frombuffer( trace[ 'r' ], dtype = numpy.uint8 ) ) ]

    self.job.board.hdf5_set_data( fd, ks, i, trace )
    self.job.scope.hdf5_set_data( fd, ks, i, trace )

    for ( k, f ) in T :
      if ( ( k in ks ) and ( k in trace ) ) :
        fd[ k ][ i ] = f( trace )

  # Driver policy: user-driven

  def _policy_user( self, fd ) :
    pass

  # Driver policy: TVLA-driven

  def _policy_tvla( self, fd ) :
    pass

  # Acquire data wrt. this driver

  def acquire( self, x = None ) :
    pass

  # Prepare the driver

  def prepare( self ) : 
    if ( not sca3s_be.share.version.match( self.job.board.driver_version ) ) :
      raise Exception( 'inconsistent driver version'    )
    if ( self.job.board.driver_id != self.driver_id ) :
      raise Exception( 'inconsistent driver identifier' )

    kernel_sizeof_x = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '?data x' ) ), 2 ** 8 )
    kernel_sizeof_r = sca3s_be.share.util.seq2int( sca3s_be.share.util.octetstr2str( self.job.board.interact( '?data r' ) ), 2 ** 8 )

    self.job.log.info( '?data x -> kernel sizeof( r ) = %s', kernel_sizeof_x )
    self.job.log.info( '?data r -> kernel sizeof( k ) = %s', kernel_sizeof_r )

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
    if   ( self.job.job_type == 'user'    ) :
      pass
    elif ( self.job.job_type == 'ci'      ) :
      pass
    elif ( self.job.job_type == 'contest' ) :
      pass

    self.job.exec_native( [ 'gzip', '--quiet', os.path.join( self.job.path, 'acquire.hdf5' ) ] )
