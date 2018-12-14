#!/bin/bash

# check configuration
if [ -z ${ACQUIRE_HOME} ] ; then
  echo "ACQUIRE_HOME environment variable undefined: aborting" ; exit
fi

# activate environment
source ${ACQUIRE_HOME}/venv/bin/activate

# execute
PYTHONPATH="${PYTHONPATH}:${ACQUIRE_HOME}/src" python3 -m acquire.main "${@}"
