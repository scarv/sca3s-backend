# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share

import abc, gzip, os, pickle, sys

class Trace( object ) :
  def __init__( self, signal_trigger, signal_acquire, data_in = None , data_out = None ) :
    super().__init__()  

    self.signal_trigger = signal_trigger
    self.signal_acquire = signal_acquire

    self.data_in        = data_in
    self.data_out       = data_out

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

    pickle.dump( trace.data_in,        fd )
    pickle.dump( trace.data_out,       fd )
     
    fd.close()

    self.traces += 1

  def  close( self ) :
    pass

class TraceSetTRS( TraceSet ) :
  def __init__( self ) :
    super().__init__()  

  def   open( self ) :
    pass

  def update( self, trace ) :
    pass

  def  close( self ) :
    pass
