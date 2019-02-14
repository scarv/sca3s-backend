#!/bin/bash

# check configuration
if [ -z ${REPO_HOME} ] ; then
  echo "REPO_HOME environment variable undefined: aborting" ; exit
fi

# activate environment
source ${REPO_HOME}/venv/bin/activate

# execute
PYTHONPATH="${PYTHONPATH}:${REPO_HOME}/src" python3 -m acquire.main "${@}"
