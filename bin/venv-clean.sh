#!/bin/bash

# check configuration
if [ -z ${REPO} ] ; then
  echo "REPO environment variable undefined: aborting" ; exit
fi

# remove environment
rm -rf ${REPO}/venv
