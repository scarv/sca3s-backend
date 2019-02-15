to  finish:

- finish up TRS trace set implementation
- allow flask configuration from some source, e.g., another file?
- cycle count capture (e.g., via systick: need to upgrade the SCALE
  BSPs first)
- generalised picoscope support; check via 5444B
- move credentials to configuration rather than environment, i.e.,

  'AWS_ACCESS_KEY_ID'
  'AWS_ACCESS_KEY'
  'AWS_REGION_ID'
  'AUTH0_CLIENT_SECRET'

- fix server waiting time to configuration
- reintegrate or remove flask-based server

to resolve:

- submit the configuration to infrastructure to "register" that is
  what is available; then request jobs wrt. ID returned

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
