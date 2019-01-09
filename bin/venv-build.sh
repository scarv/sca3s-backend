#!/bin/bash

# check configuration
if [ -z ${REPO} ] ; then
  echo "REPO environment variable undefined: aborting" ; exit
fi

# create   environment
python3 -m venv --clear ${REPO}/venv

# activate environment
source ${REPO}/venv/bin/activate

# populate environment
python3 -m pip install --upgrade pip
python3 -m pip install -r ${REPO}/requirements.txt
