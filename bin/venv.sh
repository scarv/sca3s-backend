#!/bin/bash

if [ -z ${REPO_HOME} ] ; then
  echo "REPO_HOME environment variable undefined: aborting" ; exit
fi

# create   environment
python3 -m venv --clear ${REPO_HOME}/build/venv

# activate environment
source ${REPO_HOME}/build/venv/bin/activate

# populate environment
python3 -m pip install --upgrade pip
python3 -m pip install -r ${REPO_HOME}/requirements.txt
