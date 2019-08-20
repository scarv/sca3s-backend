# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share

from acquire import board  as board
from acquire import scope  as scope
from acquire import driver as driver

from acquire import repo   as repo
from acquire import depo   as depo

import abc, binascii, csv, glob, os, pickle, sys, trsfile

class Trace( abc.ABC ) :
  def __init__( self, job ) :
    super().__init__()  

    self.job            = job

    self.trace_spec     = self.job.conf.get( 'trace-spec' )

    self.trace_content  =       self.trace_spec.get( 'content'  )
    self.trace_crop     = bool( self.trace_spec.get( 'crop'     ) )
    self.trace_compress = bool( self.trace_spec.get( 'compress' ) )

  def _prepare( self, trace ) :
    l = share.util.measure( share.util.MEASURE_MODE_DURATION, trace[ 'trigger' ], self.job.scope.channel_trigger_threshold )

    self.job.log.info( 'measure via TSC    => {0:d}'.format( trace[ 'tsc' ] ) )
    self.job.log.info( 'measure via signal => {0:g}'.format( l              ) )

    if ( self.trace_crop ) :
      edge_pos = share.util.measure( share.util.MEASURE_MODE_TRIGGER_POS, trace[ 'trigger' ], self.job.scope.channel_trigger_threshold )
      edge_neg = share.util.measure( share.util.MEASURE_MODE_TRIGGER_NEG, trace[ 'trigger' ], self.job.scope.channel_trigger_threshold )

      self.job.log.info( 'crop wrt. +ve trigger edge @ {0:d}'.format( edge_pos ) )
      self.job.log.info( 'crop wrt. -ve trigger edge @ {0:d}'.format( edge_neg ) )

      trace[ 'trigger' ] = trace[ 'trigger' ][ edge_pos : edge_neg ]
      trace[ 'signal'  ] = trace[ 'signal'  ][ edge_pos : edge_neg ]

  @abc.abstractmethod
  def   open( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def update( self, trace, i, n ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def  close( self ) :
    raise NotImplementedError()

class TracePKL( Trace ) :
  def __init__( self, job ) :
    super().__init__( job )  

  def   open( self, n ) :
    if ( not os.path.exists( './trace' ) ) :
      os.mkdir( './trace' )

  def update( self, trace, i, n ) :
    self._prepare( trace )

    fd = open( os.path.join( './trace', '%08X.pkl' % ( i ) ), 'wb' )

    for item in self.trace_content :      
      pickle.dump( trace[ item ], fd )

    fd.close()

  def  close( self ) :
    if ( self.trace_compress ) :
      for f in glob.glob( './trace/*.pkl' ) :
        self.job.run( [ 'gzip', '--quiet', f ] )

class TraceCSV( Trace ) :
  def __init__( self, job ) :
    super().__init__( job )  

  def   open( self, n ) :
    self.fd = open( './trace.csv', 'w' ) ; self.writer = csv.writer( self.fd, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_ALL )

  def update( self, trace, i, n ) :
    self._prepare( trace )

    data = list()

    for item in self.trace_content :
      if   ( item == 'trigger' ) :
        data += [ x for x in        trace[ item ] ]
      elif ( item == 'signal'  ) :
        data += [ x for x in        trace[ item ] ]
      elif ( item == 'tsc'     ) :
        data += [                   trace[ item ] ]
      else :
        data += [ binascii.b2a_hex( trace[ item ] ).decode() ]

    self.writer.writerow( data )

  def  close( self ) :
    self.fd.close()

    if ( self.trace_compress ) :
      self.job.run( [ 'gzip', '--quiet', './trace.csv' ] )

class TraceTRS( Trace ) :
  def __init__( self, job ) :
    super().__init__( job )  

  def   open( self, n ) :
    self.fd = trsfile.open( './trace.trs', 'w', padding_mode = trsfile.TracePadding.AUTO )

  def update( self, trace, i, n ) :
    self._prepare( trace )

    data = bytes()

    for item in self.trace_content :
      if   ( item == 'trigger' ) :
        continue
      elif ( item == 'signal'  ) :
        continue   
      elif ( item == 'tsc'     ) :
        data += bytes( struct.pack( '<Q', trace[ item ] ) )
      else :
        data += bytes(                    trace[ item ]   )

    if   ( 'trigger' in self.trace_content ) :
      self.fd.extend( [ trsfile.Trace( trsfile.SampleCoding.FLOAT, trace[ 'trigger' ], data = data ) ] )
    elif ( 'signal'  in self.trace_content ) :
      self.fd.extend( [ trsfile.Trace( trsfile.SampleCoding.FLOAT, trace[ 'signal'  ], data = data ) ] )

  def  close( self ) :
    self.fd.close()

    if ( self.trace_compress ) :
      self.job.run( [ 'gzip', '--quiet', './trace.trs' ] )
