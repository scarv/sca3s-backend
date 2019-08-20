#!/bin/bash

if [ -z ${REPO_HOME} ] ; then
  echo "REPO_HOME environment variable undefined: aborting" ; exit
fi

source ${REPO_HOME}/build/venv/bin/activate

PYTHONPATH="${PYTHONPATH}:${REPO_HOME}/src:${REPO_HOME}/extern/sca3s-spec/src" python3 -m server.main --sys:type="acquire" "${@}"
