# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import datetime, h5py, matplotlib as mpl, matplotlib.pyplot as plt, numpy, os, pylatex, scipy.stats, shutil

mpl.rc( 'text', **{ 'usetex' : True, 'latex.preamble' : r'\usepackage{pxfonts}' } )
mpl.rc( 'font', **{ 'family' : 'serif'                                          } )

class Report( pylatex.Document ) :
  def __init__( self, job ) :
    super().__init__( geometry_options = { 'a4paper' : True, 'margin' : '2cm' } )

    self.job = job

  # LaTeX-related support functionality (supplementing, e.g., pylatex.util).

  def href( self, url, text = None ) :
    if ( text == None ) :
      text = url

    return pylatex.NoEscape( r'\href{' + str( url ) + r'}{\texttt{' + pylatex.escape_latex( str( text ) ) + r'}}' )

  def tt( self, text ) :
    return pylatex.NoEscape( r'{\tt ' + pylatex.escape_latex( str( text ) ) + '}' )

  # Compile document, i.e., LaTeX -> PDF.

  def compile( self, pdf ) :
    if ( not os.path.isdir( os.path.join( self.job.path, 'report' ) ) ) :
      os.mkdir( os.path.join( self.job.path, 'report' ) )

    try :
      self.generate_pdf( os.path.join( self.job.path, 'report', 'report' ), compiler = 'pdflatex', silent = True, clean = False, clean_tex = False )
    except Exception as e :
      raise Exception( 'failed to compile report' )

    shutil.copyfile( os.path.join( self.job.path, 'report', 'report.pdf' ), pdf )

  # Emit document preamble:
  # 
  # 1. include any required packages
  # 2. configure page style (i.e., header and footer)

  def emit_preamble( self ) :
    self.packages.append( pylatex.Package(  'amsmath', options = []                   ) )
    self.packages.append( pylatex.Package(  'amssymb', options = []                   ) )
    self.packages.append( pylatex.Package(  'fontenc', options = [ 'T1'             ] ) )
    self.packages.append( pylatex.Package( 'hyperref', options = [ 'hidelinks=true' ] ) )
    self.packages.append( pylatex.Package(  'pxfonts', options = []                   ) )
    self.packages.append( pylatex.Package(   'xcolor', options = []                   ) )

    style = pylatex.PageStyle( 'style', header_thickness = 1.0, footer_thickness = 1.0 )

    with style.create( pylatex.Head( 'C' ) ) as head_c :
      pass

    with style.create( pylatex.Head( 'L' ) ) as head_l :
      pass

    with style.create( pylatex.Head( 'R' ) ) as head_r :
      pass

    with style.create( pylatex.Foot( 'C' ) ) as foot_c :
      pass

    with style.create( pylatex.Foot( 'L' ) ) as foot_l :
      foot_l.append( self.href( r'https://sca3s.scarv.org' ) )
      foot_l.append( pylatex.Math( inline = True, data = pylatex.NoEscape( r'~~\subset~~' ) ) )
      foot_l.append( self.href( r'https://scarv.org'       ) )

    with style.create( pylatex.Foot( 'R' ) ) as foot_r :
      foot_r.append( pylatex.NoEscape( r'\thepage' ) )

    self.preamble.append( style ) ; self.change_document_style( 'style' )

  # Emit document prologue:
  # 
  # 1. banner logo and text
  # 2. acquisition details, i.e.,
  #    - version
  #    - timestamp
  #    - repo
  #    - board
  #    - scope
  #    - driver

  def emit_prologue( self ) :
    self.append( pylatex.NewPage() )

    with self.create( pylatex.Figure( position = 'h!' ) ) as fig :
      fig.add_image( sca3s_be.share.sys.conf.get( 'logo', section = 'path' ), width = pylatex.NoEscape( r'0.5\textwidth' ) )

      fig.append( pylatex.NoEscape( r'\\ [1.0cm]' ) )
      fig.append( pylatex.NoEscape( r'{\LARGE\bf ' +          ( r'SCA3S: side-channel analysis as a service' ) + r'}' ) )
      fig.append( pylatex.NoEscape( r'\\ [0.5cm]' ) )
      fig.append( pylatex.NoEscape( r'{\LARGE\bf ' + self.href( r'https://sca3s.scarv.org'                   ) + r'}' ) )
      fig.append( pylatex.NoEscape( r'\\ [1.0cm]' ) )

      with fig.create( pylatex.Tabular( pylatex.NoEscape( r'rcl' ) ) ) as table :
        table.add_row( ( self.tt( r'  version' ), ':', self.tt( sca3s_be.share.version.ident()                 ) ) )
        table.add_row( ( self.tt( r'timestamp' ), ':', self.tt( datetime.datetime.now( datetime.timezone.utc ) ) ) )
        table.add_empty_row()
        table.add_row( ( self.tt( r'     repo' ), ':', self.tt( str( self.job.repo   )                         ) ) )
        table.add_empty_row()
        table.add_row( ( self.tt( r'    board' ), ':', self.tt( str( self.job.board  )                         ) ) )
        table.add_row( ( self.tt( r'    scope' ), ':', self.tt( str( self.job.scope  )                         ) ) )
        table.add_empty_row()
        table.add_row( ( self.tt( r'   driver' ), ':', self.tt( str( self.job.driver )                         ) ) )

  # Emit document epilogue.

  def emit_epilogue( self ) :
    pass

  # Emit document content: calibration report.

  def emit_section_calibrate( self ) :
    def render( fd, width = 1.0 ) :
      # step #2: generate plot
  
      plt.xlabel( r'{\tt sample }' )
  
      ys = numpy.array( fd[ 'trace/signal'  ][ 0 ] )
      xs = numpy.arange( 0, len( ys ) )
  
      plt.plot( xs, ys, 'tab:blue' )
  
      ys = numpy.array( fd[ 'trace/trigger' ][ 0 ] )
      xs = numpy.arange( 0, len( ys ) )
  
      plt.plot( xs, ys, 'tab:red'  )
  
      # step #3: generate LaTeX
  
      fig = pylatex.Figure( position = 'h!' )
  
      fig.add_plot( width = pylatex.NoEscape( r'%f\textwidth' % ( width ) ) )

      # step #4: clean-up and return result

      plt.close() ; return fig

    self.append( pylatex.NewPage() )

    with self.create( pylatex.Section( 'Calibration report' ) ) :
      with self.create( pylatex.Subsection( 'Step 1: large trial(s)' ) ) :
        if ( not os.path.isfile( os.path.join( self.job.path, 'calibrate', 'calibrate-step_1.hdf5' ) ) ) :
          raise Exception()

        with h5py.File( os.path.join( self.job.path, 'calibrate', 'calibrate-step_1.hdf5' ), 'r' ) as fd :
          if ( not 'trace/trigger' in fd ) :
            raise Exception()
          if ( not 'trace/signal'  in fd ) :
            raise Exception()
      
          self.append( render( fd, width = 0.5 ) )

      with self.create( pylatex.Subsection( 'Step 2: small trial(s)' ) ) :
        if ( not os.path.isfile( os.path.join( self.job.path, 'calibrate', 'calibrate-step_2.hdf5' ) ) ) :
          raise Exception()

        with h5py.File( os.path.join( self.job.path, 'calibrate', 'calibrate-step_2.hdf5' ), 'r' ) as fd :
          if ( not 'trace/trigger' in fd ) :
            raise Exception()
          if ( not 'trace/signal'  in fd ) :
            raise Exception()
      
          self.append( render( fd, width = 0.5 ) )

      with self.create( pylatex.Subsection( 'Step 3: final trial(s)' ) ) :
        if ( not os.path.isfile( os.path.join( self.job.path, 'calibrate', 'calibrate-step_3.hdf5' ) ) ) :
          raise Exception()

        with h5py.File( os.path.join( self.job.path, 'calibrate', 'calibrate-step_3.hdf5' ), 'r' ) as fd :
          if ( not 'trace/trigger' in fd ) :
            raise Exception()
          if ( not 'trace/signal'  in fd ) :
            raise Exception()
      
          self.append( render( fd, width = 0.5 ) )

  # Emit document content: latency     report.

  def emit_section_latency( self ) :
    def render( fd, width = 1.0, metric = 'cycle' ) :
      # step #1: compute
    
      ys = numpy.array( fd[ 'perf/%s' % ( metric ) ] )
      xs = numpy.arange( 0, len( ys ) )
  
      t_min  = float( min( ys ) )
      t_max  = float( max( ys ) )
      t_mean = float( sum( ys ) ) / len( ys )
  
      # step #2: generate plot
  
      plt.xlabel( r'{\tt trace  }' )
      plt.ylabel( r'{\tt latency}' )
  
      plt.gca().yaxis.set_major_locator( plt.MaxNLocator( integer = True ) )
      plt.gca().xaxis.set_major_locator( plt.MaxNLocator( integer = True ) )
  
      plt.axhline( t_min, color = 'tab:gray', linestyle = ':' )
      plt.axhline( t_max, color = 'tab:gray', linestyle = ':' )
  
      plt.plot( xs, ys, '.', color = 'tab:blue' )
  
      # step #3: generate LaTeX
  
      fig = pylatex.Figure( position = 'h!' )
  
      fig.add_plot( width = pylatex.NoEscape( r'%f\textwidth' % ( width ) ) )
      
      tab = pylatex.Tabular( pylatex.NoEscape( 'rcl' ) )
  
      tab.add_row( ( self.tt( ' min' ), ':', pylatex.Math( inline = True, data = '%.2f' % ( t_min  ) ) ) )
      tab.add_row( ( self.tt( ' max' ), ':', pylatex.Math( inline = True, data = '%.2f' % ( t_max  ) ) ) )
      tab.add_row( ( self.tt( 'mean' ), ':', pylatex.Math( inline = True, data = '%.2f' % ( t_mean ) ) ) )
  
      # step #4: clean-up and return result
  
      plt.close() ; return ( fig, tab )

    self.append( pylatex.NewPage() )

    with self.create( pylatex.Section( 'Latency report' ) ) :
      with self.create( pylatex.Subsection( 'Cycle'    ) ) :
        with h5py.File( os.path.join( self.job.path, 'acquire.hdf5' ), 'r' ) as fd :
          if ( not 'perf/cycle'    in fd ) :
            raise Exception()

          ( fig, tab ) = render( fd, width = 0.5, metric = 'cycle'    )

          self.append( fig )
          self.append( tab )

      with self.create( pylatex.Subsection( 'Duration'  ) ) :
        with h5py.File( os.path.join( self.job.path, 'acquire.hdf5' ), 'r' ) as fd :
          if ( not 'perf/duration' in fd ) :
            raise Exception()

          ( fig, tab ) = render( fd, width = 0.5, metric = 'duration' )

          self.append( fig )
          self.append( tab )

  # Emit document content: leakage     report.

  def emit_section_leakage( self ) :
    def render( fd, width = 1.0 ) :
      def trace( fd, i ) :
        return fd[ 'trace/signal' ][ fd[ 'crop/signal' ][ i ] ][ 0 ]
    
      def patch( xs, ys, threshold = 0 ) :
        xr = list()
        yr = list()
    
        for i in range( 1, len( xs ) ) :
          x_0 = xs[ i - 1 ] ; y_0 = ys[ i - 1 ] ;
          x_1 = xs[ i     ] ; y_1 = ys[ i     ]
    
          if   ( ( y_0 < threshold ) and ( y_1 > threshold ) ) :
            xr.append( x_0 + ( ( x_1 - x_0 ) / 2 ) )
            yr.append( threshold )
          elif ( ( y_0 > threshold ) and ( y_1 < threshold ) ) :
            xr.append( x_0 + ( ( x_1 - x_0 ) / 2 ) )
            yr.append( threshold )
    
          xr.append( x_1 )
          yr.append( y_1 )
    
        return ( numpy.array( xr ), numpy.array( yr ) )
  
      # step #1: compute
  
      for ( i, t ) in enumerate( fd[ 'trace/signal' ] ) :
        l = len( trace( fd, i ) )
        
        if   ( i == 0 ) :
          crop = l
        elif ( i >  0 ) :
          crop = l if ( l < crop ) else crop    
        
      lhs = numpy.array( [ trace( fd, i )[ 0 : crop ] for i in fd[ 'tvla' ][ 'lhs' ] ] )
      rhs = numpy.array( [ trace( fd, i )[ 0 : crop ] for i in fd[ 'tvla' ][ 'rhs' ] ] )
        
      ys  = numpy.nan_to_num( scipy.stats.ttest_ind( lhs, rhs, axis = 0, equal_var = False )[ 0 ] )
      xs  = numpy.arange( 0, len( ys ) )
      
      threshold_lo = -4.5 ; fail_lo = len( numpy.where( ys < threshold_lo )[ 0 ] )
      threshold_hi = +4.5 ; fail_hi = len( numpy.where( ys > threshold_hi )[ 0 ] )
  
      result       = ( fail_lo + fail_hi ) > 0
  
      # step #2: generate plot
  
      plt.xlabel( r'{\tt sample     }' )
      plt.ylabel( r'{\tt t-statistic}' )
    
      ( xs, ys ) = patch( xs, ys, threshold = threshold_lo )
      ( xs, ys ) = patch( xs, ys, threshold = threshold_hi )
          
      ts = numpy.copy( ys ) ; ts[ ( ys < threshold_lo ) | ( ys > threshold_hi ) ] = numpy.nan        
      plt.plot( xs, ts, color = 'tab:green' )
      ts = numpy.copy( ys ) ; ts[ ( ys > threshold_lo )                         ] = numpy.nan        
      plt.plot( xs, ts, color = 'tab:red'   )
      ts = numpy.copy( ys ) ; ts[                         ( ys < threshold_hi ) ] = numpy.nan        
      plt.plot( xs, ts, color = 'tab:red'   )
  
      plt.axhline( threshold_lo, color = 'tab:gray', linestyle = ':' )
      plt.axhline( threshold_hi, color = 'tab:gray', linestyle = ':' )
  
      # step #3: generate LaTeX
  
      fig = pylatex.Figure( position = 'h!' )
  
      fig.add_plot( width = pylatex.NoEscape( r'%f\textwidth' % ( width ) ) )
  
      tab = pylatex.Tabular( pylatex.NoEscape( 'ccccrcr' ) )
    
      tab.add_row( ( self.tt( r'  samples' ), 
                     pylatex.Math( inline = True, data = '<' ),
                     self.tt( r'threshold' ), 
                     pylatex.Math( inline = True, data = '=' ), 
                     pylatex.Math( inline = True, data = '%+.2f' % ( threshold_lo ) ), ':', pylatex.Math( inline = True, data = fail_lo ) ) )
      tab.add_row( ( self.tt( r'  samples' ), 
                     pylatex.Math( inline = True, data = '>' ),
                     self.tt( r'threshold' ), 
                     pylatex.Math( inline = True, data = '=' ), 
                     pylatex.Math( inline = True, data = '%+.2f' % ( threshold_hi ) ), ':', pylatex.Math( inline = True, data = fail_hi ) ) )
    
      tab.add_empty_row()  
    
      tab.add_row( ( '', '', '', '', '', pylatex.Math( inline = True, data = pylatex.NoEscape( r'\Rightarrow' ) ), pylatex.NoEscape( r'\textcolor{red}{fail}' if ( result ) else r'\textcolor{green}{pass}' ) ) )
  
      # step #4: clean-up and return result
  
      plt.close() ; return ( fig, tab )

    self.append( pylatex.NewPage() )
  
    with self.create( pylatex.Section( 'Leakage report' ) ) :
      with h5py.File( os.path.join( self.job.path, 'acquire.hdf5' ), 'r' ) as fd :
        if ( not 'trace/signal' in fd ) :
          raise Exception()
        if ( not  'crop/signal' in fd ) :
          raise Exception()
        
        if ( not 'tvla/lhs'     in fd ) :
          raise Exception()
        if ( not 'tvla/rhs'     in fd ) :
          raise Exception()

        ( fig, tab ) = render( fd, width = 0.9 )

        self.append( fig )
        self.append( tab )
