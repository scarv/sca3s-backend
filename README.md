# [`lab.scarv.org`](https://github.com/scarv/lab.scarv.org.git): acquire framework

<!--- -------------------------------------------------------------------- --->

[![Build Status](https://travis-ci.com/scarv/lab-acquire.svg)](https://travis-ci.com/scarv/lab-acquire)
[![Documentation](https://codedocs.xyz/scarv/lab-acquire.svg)](https://codedocs.xyz/scarv/lab-acquire)

<!--- -------------------------------------------------------------------- --->

*A component part of the
[SCARV](https://github.com/scarv)
project,
`lab.scarv.org` is a collection of resources that support the
development and analysis of cryptographic implementations wrt.
[side-channel attack](https://en.wikipedia.org/wiki/Side-channel_attack):
it places particular emphasis on analogue side-channels (e.g.,
power and EM) stemming from
[RISC-V](https://riscv.org)-based
platforms.
The main
[repository](https://github.com/scarv/xcrypto)
acts as a general container for associated resources;
this specific submodule houses
the framework tasked with orchestrating the acquisition of traces.*

<!--- -------------------------------------------------------------------- --->


<!--- -------------------------------------------------------------------- --->

## Acknowledgements

This work has been supported in part by EPSRC via grant 
[EP/R012288/1](https://gow.epsrc.ukri.org/NGBOViewGrant.aspx?GrantRef=EP/R012288/1),
under the [RISE](http://www.ukrise.org) programme.

<!--- -------------------------------------------------------------------- --->

to  finish:

- sort out some sensible deployment strategy
- move credentials to configuration rather than environment, i.e.,

  'AWS_ACCESS_KEY_ID'
  'AWS_ACCESS_KEY'
  'AWS_REGION_ID'
  'AUTH0_CLIENT_SECRET'

- fix server waiting time to configuration
- reintegrate or remove flask-based server

- finish up TRS trace set implementation
- generalised picoscope support; check via 5444B

to resolve:

- the source code is currently totally undocumented :-/

- the management of exceptions is currently less than ideal: there
  are two central issues, namely

  1) the generation of "rich" exceptions (vs. just *an* exception),
  2) the management of those exceptions, e.g., to allow a graceful
     and well-logged action.

- there is currently an informal policy that restricts the per job 
  log to INFO level only: there are never any DEBUG entries.  this
  is to prevent exposure of low level information about the server
  in the per job log, which is, after all available to the user.
  
  on the other hand, this is informal: information might still be
  exposed.  examples:

  - (temporary) job path via external commands (e.g., git),
  - environment variables currently)allowed in job manifest.

  a more precise and fail-safe way to manage this would be great.
