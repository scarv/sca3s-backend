#!/bin/bash

# check configuration
if [ -z ${ACQUIRE_HOME} ] ; then
  echo "ACQUIRE_HOME environment variable undefined: aborting" ; exit
fi

# remove environment
rm -rf ${ACQUIRE_HOME}/venv
