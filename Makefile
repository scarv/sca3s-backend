# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

ifndef REPO_HOME
  $(error "execute 'source ./bin/conf.sh' to configure environment")
endif

# =============================================================================

# Set defaults for various required environment variables.

export CONTEXT ?= native

# =============================================================================

ifeq "${CONTEXT}" "docker"

endif

ifeq "${CONTEXT}" "native"
acquire  :
	@PYTHONPATH="${PYTHONPATH}:${REPO_HOME}/src:${REPO_HOME}/extern/sca3s-spec/src" python3 -m sca3s.backend.main ${@}

analyse  :
	@PYTHONPATH="${PYTHONPATH}:${REPO_HOME}/src:${REPO_HOME}/extern/sca3s-spec/src" python3 -m sca3s.backend.main ${@}

venv     : ${REPO_HOME}/requirements.txt
	@${REPO_HOME}/bin/venv.sh

doc      : ${REPO_HOME}/Doxyfile
	@doxygen ${<}

clean    :
	@rm --force --recursive ${REPO_HOME}/build/*

spotless : clean
	@rm --force --recursive ${REPO_HOME}/data/git/*
	@rm --force --recursive ${REPO_HOME}/data/job/*
	@rm --force --recursive ${REPO_HOME}/data/log/*
endif

# =============================================================================
