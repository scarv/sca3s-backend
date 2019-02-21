# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

ifndef REPO_HOME
  $(error "execute 'source ./bin/conf.sh' to configure environment")
endif

example-cli :
	@${REPO_HOME}/bin/acquire.sh --sys:mode=cli --sys:conf=${REPO_HOME}/example/example.conf --job:manifest-file=${REPO_HOME}/example/example.job

example-server-push_device :
	@curl localhost:5000/api/device --header 'Content-Type: application/json' 
example-server-push_submit :
	@curl localhost:5000/api/submit --header 'Content-Type: application/json' --data @${REPO_HOME}/example/example.job

clean    :
	@rm -rf ${REPO_HOME}/data/job/*
	@rm -rf ${REPO_HOME}/data/log/*

spotless : clean
	@rm -rf ${REPO_HOME}/build/*
