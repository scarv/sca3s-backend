#!/bin/bash

# Copyright (C) 2019 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which
# can be found at https://opensource.org/licenses/MIT (or should be included
# as LICENSE.txt within the associated archive or repository).

if [ -z ${REPO_HOME} ] ; then
  echo "REPO_HOME environment variable undefined: aborting" ; exit
fi

export PYTHONPATH="${PYTHONPATH}:${REPO_HOME}/src:${REPO_HOME}/extern/sca3s-spec/src" 

python3 -m sca3s_backend.main ${@}
