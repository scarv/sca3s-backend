#!/bin/bash

# check configuration
if [ -z ${REPO} ] ; then
  echo "REPO environment variable undefined: aborting" ; exit
fi

# activate environment
source ${REPO}/venv/bin/activate

# execute
PYTHONPATH="${PYTHONPATH}:${REPO}/src" python3 -m acquire.main "${@}"
