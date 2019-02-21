# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share

import abc, gzip, os, pickle, sys, trsfile

class Trace( object ) :
  def __init__( self, signal_trigger, signal_acquire, tsc = None, data_i = None , data_o = None ) :
    super().__init__()  

    self.signal_trigger = signal_trigger
    self.signal_acquire = signal_acquire

    self.tsc            = tsc

    self.data_i         = data_i
    self.data_o         = data_o

class TraceSet( abc.ABC ) :
  def __init__( self ) :
    super().__init__()  

  @abc.abstractmethod
  def   open( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def update( self ) :
    raise NotImplementedError()

  @abc.abstractmethod
  def  close( self ) :
    raise NotImplementedError()

class TraceSetPickle( TraceSet ) :
  def __init__( self ) :
    super().__init__()  

  def   open( self ) :
    if ( not os.path.exists( './trace' ) ) :
      os.mkdir( './trace' )

    self.traces = 0

  def update( self, trace ) :
    fd = gzip.open( os.path.join( './trace', '%08X.pkl.gz' % ( self.traces ) ), 'wb' )
      
    pickle.dump( trace.signal_trigger, fd )
    pickle.dump( trace.signal_acquire, fd )

    pickle.dump( trace.data_i,         fd )
    pickle.dump( trace.data_o,         fd )
     
    fd.close()

    self.traces += 1

  def  close( self ) :
    pass

class TraceSetTRS( TraceSet ) :
  def __init__( self ) :
    super().__init__()  

  def   open( self ) :
    self.fd = trsfile.create( 'trace.trs', trsfile.TracePadding.PAD, force_overwrite = True )

  def update( self, trace ) :
    def conv( data ) :
      r = bytearray()

      for key in sorted( data.keys() ) :
        r += data[ key ]

      return r

    data_i  = conv( trace.data_i )
    data_o  = conv( trace.data_o )

    data    = data_i + data_o

    headers = { trsfile.Header.INPUT_OFFSET  : 0,
                trsfile.Header.INPUT_LENGTH  : len( data_i ),
                trsfile.Header.OUTPUT_OFFSET : len( data_i ),
                trsfile.Header.OUTPUT_OFFSET : len( data_o ) }

    self.fd.extend( [ trsfile.Trace( trsfile.SampleCoding.FLOAT, trace.signal_acquire, data = data, headers = headers ) ] )

  def  close( self ) :
    self.fd.close()
