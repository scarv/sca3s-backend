#!/bin/bash

# check configuration
if [ -z ${ACQUIRE_HOME} ] ; then
  echo "ACQUIRE_HOME environment variable undefined: aborting" ; exit
fi

# create   environment
python3 -m venv --clear ${ACQUIRE_HOME}/venv

# activate environment
source ${ACQUIRE_HOME}/venv/bin/activate

# populate environment
python3 -m pip install --upgrade pip
python3 -m pip install -r ${ACQUIRE_HOME}/requirements.txt
