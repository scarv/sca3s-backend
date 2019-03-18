# [`lab.scarv.org`](https://github.com/scarv/lab.scarv.org.git): acquisition appliance

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
├── bin                     - scripts (e.g., environment configuration)
├── build                   - working directory for build
└── src                     - source code
```

<!--- -------------------------------------------------------------------- --->

## TODO

- generalised picoscope support; check via 5444B
- sort out some sensible deployment strategy
- the source code is currently totally undocumented :-/

<!--- -------------------------------------------------------------------- --->

## Acknowledgements

This work has been supported in part by EPSRC via grant 
[EP/R012288/1](https://gow.epsrc.ukri.org/NGBOViewGrant.aspx?GrantRef=EP/R012288/1),
under the [RISE](http://www.ukrise.org) programme.

<!--- -------------------------------------------------------------------- --->
