#!/bin/bash

if [ -z ${REPO_HOME} ] ; then
  echo "REPO_HOME environment variable undefined: aborting" ; exit
fi

# remove environment
rm -rf ${REPO_HOME}/build/venv
