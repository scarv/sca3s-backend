# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

# Per                                                                                                                                                                                                                                         
#                                                                                                                                                                                                                                             
# https://www.python.org/dev/peps/pep-0420/#id22                                                                                                                                                                                              
#                                                                                                                                                                                                                                             
# we want to support a "split" (per component) sca3s namespace: by default,                                                                                                                                                                   
# Python uses the first one in ${PYTHONPATH} exclusively.  This is achieved                                                                                                                                                                   
# by extending the search path.

from pkgutil import extend_path
__path__ = extend_path( __path__, __name__ )

__all__ = [ 'backend' ]

from . import backend

