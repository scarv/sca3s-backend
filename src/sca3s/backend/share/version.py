# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from sca3s import backend    as sca3s_be
from sca3s import middleware as sca3s_mw

import os

VERSION_MAJOR = os.environ[ 'REPO_VERSION_MAJOR' ]
VERSION_MINOR = os.environ[ 'REPO_VERSION_MINOR' ]
VERSION_PATCH = os.environ[ 'REPO_VERSION_PATCH' ]

VERSION       = os.environ[ 'REPO_VERSION'       ]
