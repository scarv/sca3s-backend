# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

example-device:
	@curl localhost:5000/api/device --header 'Content-Type: application/json' 
example-submit:
	@curl localhost:5000/api/submit --header 'Content-Type: application/json' --data @./example/example.job

spotless :
	@find ./src -name __pycache__ -type d -exec rm -rf {} \;
