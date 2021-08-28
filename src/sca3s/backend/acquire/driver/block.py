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

import binascii, h5py, numpy

class DriverImp( driver.DriverAbs ) :
  def __init__( self, job ) :
    super().__init__( job )
   
  def hdf5_add_attr( self, fd              ) :
    spec = [ ( 'kernel/sizeof_k',      self.job.board.kernel.sizeof_k,   '<u8' ),
             ( 'kernel/sizeof_m',      self.job.board.kernel.sizeof_m,   '<u8' ),
             ( 'kernel/sizeof_c',      self.job.board.kernel.sizeof_c,   '<u8' ) ]

    self.job.board.hdf5_add_attr( self.trace_content, fd              )
    self.job.scope.hdf5_add_attr( self.trace_content, fd              )

    sca3s_be.share.util.hdf5_add_attr( spec, self.trace_content, fd              )

  def hdf5_add_data( self, fd, n           ) :
    spec = [ (   'data/k',        ( n, self.job.board.kernel.sizeof_k ), 'B'   ),
             (   'data/usedof_k', ( n,                                ), '<u8' ),
             (   'data/m',        ( n, self.job.board.kernel.sizeof_m ), 'B'   ),
             (   'data/usedof_m', ( n,                                ), '<u8' ),
             (   'data/c',        ( n, self.job.board.kernel.sizeof_c ), 'B'   ),
             (   'data/usedof_c', ( n,                                ), '<u8' ) ]

    self.job.board.hdf5_add_data( self.trace_content, fd, n           )
    self.job.scope.hdf5_add_data( self.trace_content, fd, n           )

    sca3s_be.share.util.hdf5_add_data( spec, self.trace_content, fd, n           )

  def hdf5_set_data( self, fd, n, i, trace ) :
    spec = [ (   'data/k',        lambda trace : numpy.frombuffer( trace[ 'data/k' ], dtype = numpy.uint8 ) ),
             (   'data/usedof_k', lambda trace :              len( trace[ 'data/k' ]                      ) ),
             (   'data/m',        lambda trace : numpy.frombuffer( trace[ 'data/m' ], dtype = numpy.uint8 ) ),
             (   'data/usedof_m', lambda trace :              len( trace[ 'data/m' ]                      ) ),
             (   'data/c',        lambda trace : numpy.frombuffer( trace[ 'data/c' ], dtype = numpy.uint8 ) ),
             (   'data/usedof_c', lambda trace :              len( trace[ 'data/c' ]                      ) ) ]

    self.job.board.hdf5_set_data( self.trace_content, fd, n, i, trace )
    self.job.scope.hdf5_set_data( self.trace_content, fd, n, i, trace )

    sca3s_be.share.util.hdf5_set_data( spec, self.trace_content, fd, n, i, trace )

  def prepare( self ) : 
    if ( not sca3s_be.share.version.match( self.job.board.driver_version ) ) :
      raise Exception( 'inconsistent driver version'    )
    if ( self.driver_id !=               ( self.job.board.driver_id      ) ) :
      raise Exception( 'inconsistent driver identifier' )
    
    if ( self.job.board.kernel.nameof not in [ 'generic', 'aes' ] ) :
      raise Exception( 'unsupported kernel name' )
    if ( self.job.board.kernel.modeof not in [ 'default', 'enc', 'dec' ] ) :
      raise Exception( 'unsupported kernel type' )

    if ( self.job.board.kernel.modeof == 'enc'     ) :
      if ( not ( self.job.board.kernel.data_wr_id == set( [        'esr', 'k', 'm' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )
      if ( not ( self.job.board.kernel.data_rd_id == set( [ 'fec', 'fcc',      'c' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )

    if ( self.job.board.kernel.modeof == 'dec'     ) :
      if ( not ( self.job.board.kernel.data_wr_id == set( [        'esr', 'k', 'c' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )
      if ( not ( self.job.board.kernel.data_rd_id == set( [ 'fec', 'fcc',      'm' ] ) ) ) :
        raise Exception( 'inconsistent kernel I/O spec.' )

    if ( ( self.policy_id == 'user' ) and not self.job.board.kernel.supports_policy_user( self.policy_spec ) ) :
      raise Exception( 'unsupported kernel policy' )
    if ( ( self.policy_id == 'tvla' ) and not self.job.board.kernel.supports_policy_tvla( self.policy_spec ) ) :
      raise Exception( 'unsupported kernel policy' )
