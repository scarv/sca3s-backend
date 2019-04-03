# [`lab.scarv.org`](https://github.com/scarv/lab.scarv.org): acquisition appliance

<!--- -------------------------------------------------------------------- --->

[![Build Status](https://travis-ci.com/scarv/lab-acquire.svg)](https://travis-ci.com/scarv/lab-acquire)
[![Documentation](https://codedocs.xyz/scarv/lab-acquire.svg)](https://codedocs.xyz/scarv/lab-acquire)

<!--- -------------------------------------------------------------------- --->

*Acting as a component part of the
[SCARV](https://www.scarv.org)
project,
`lab.scarv.org` is a collection of resources that support the
development and analysis of cryptographic implementations wrt.
[side-channel attack](https://en.wikipedia.org/wiki/Side-channel_attack):
it places particular emphasis on analogue side-channels (e.g.,
power and EM) stemming from
[RISC-V](https://riscv.org)-based
platforms.
The main
[repository](https://github.com/scarv/lab.scarv.org)
acts as a general container for associated resources;
this specific submodule houses
the acquisition appliance, which is, for example, tasked with orchestrating the acquisition of trace sets.*

<!--- -------------------------------------------------------------------- --->

## Organisation

```
├── bin                       - scripts (e.g., environment configuration)
├── build                     - working directory for build
├── data                      - working directory for data
├── example                   - examples (e.g., job manifests)
└── src                       - source code
    ├── acquire/depo          - depository implementations
    ├── acquire/device/board  - board      implementations
    ├── acquire/device/scope  - scope      implementations
    ├── acquire/driver        - driver     implementations
    ├── acquire/repo          - repository implementations
    ├── acquire/server        - server functionality
    └── acquire/share         - shared functionality
```

<!--- -------------------------------------------------------------------- --->

## Quickstart

1. The main `lab.scarv.org`
   [repository](https://github.com/scarv/lab.scarv.org)
   houses some overarching documentation, which offers some
   context and explanation: it *might* be sensible to start
   by reading that.

2. Install any associated pre-requisites, e.g.,

   - a board-specific compiler and programming tool-chain,
     e.g., suitable versions of
     [GCC](https://gcc.gnu.org)
     and
     [OpenOCD](http://openocd.org),
   - a scope-specific driver,
     e.g., offering a specific API for some
     [PicoScope](https://www.picotech.com/downloads)
     oscilloscope,
   - the
     [Doxygen](http://www.doxygen.nl)
     documentation generation system.

3. Execute

   ```sh
   git clone https://github.com/${USER}/lab-acquire.git
   cd ./lab-acquire
   source ./bin/conf.sh
   ```

   to clone and initialise the repository,
   then configure the environment;
   for example, you should find that the environment variable
   `REPO_HOME`
   is set appropriately.

4. Prepare various supporting material:

   1. create and populate a suitable Python
      [virtual environment](https://docs.python.org/library/venv.html)
      based on `${REPO_HOME}/requirements.txt` by executing

      ```
      make venv
      ```

   2. write a configuration file, which captures the static
      configuration of the acquisition appliance, e.g., by
      updating

      ```
      ${REPO_HOME}/example/example.conf
      ```

      so the database of hardware (namely board and scope)
      devices reflects those attached,

   3. modern versions of 
      [git-clone](https://git-scm.com/docs/git-clone)
      allow the `--reference[-if-able]` option, allowing a
      local cached replacement for some remote repository:
      preparing such a cache somewhere, e.g., in

      ```
      ${REPO_HOME}/data/git
      ```

      can significantly improve efficiency wrt. repeated
      download of common repositories.

5. Either

   1. execute the acquisition appliance directly via

      ```
      ${REPO_HOME}/bin/acquire.py
      ```

      to satisfy use-cases such as
   
      1. fulfilment of a local  job manifest,
         e.g.,
   
         ```
         ${REPO_HOME}/bin/acquire.py --sys:mode=cli         --sys:conf="${REPO_HOME}/example/example.conf" ...
         ```
   
      2. fulfilment of a remote job manifest *pushed from* some queue to the server,
         e.g.,
   
         ```
         ${REPO_HOME}/bin/acquire.py --sys:mode=server-push --sys:conf="${REPO_HOME}/example/example.conf" ...
         ```
   
      3. fulfilment of a remote job manifest *pulled from* some queue by the server,
         e.g.,
   
         ```
         ${REPO_HOME}/bin/acquire.py --sys:mode=server-pull --sys:conf="${REPO_HOME}/example/example.conf" ...
         ```

      or

   2. use targets in the top-level `Makefile` to drive a set of
      common tasks, e.g.,

      - execute
   
        ```sh
        make doc
        ```
   
        to build the documentation,
   
      - execute
   
        ```sh
        make clean
        ```
   
        to clean-up
        (e.g., remove everything built in `${REPO_HOME}/build`, and data in `${REPO_HOME}/data`).

<!--- -------------------------------------------------------------------- --->

## Acknowledgements

This work has been supported in part by EPSRC via grant 
[EP/R012288/1](https://gow.epsrc.ukri.org/NGBOViewGrant.aspx?GrantRef=EP/R012288/1),
under the [RISE](http://www.ukrise.org) programme.

<!--- -------------------------------------------------------------------- --->
