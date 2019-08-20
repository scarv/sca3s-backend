# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share

from acquire import board  as board
from acquire import scope  as scope
from acquire import driver as driver

from acquire import repo   as repo
from acquire import depo   as depo

import json, jsonschema

# this is basically the solution to a FAQ in
# 
# https://python-jsonschema.readthedocs.io
#
# which (recursively) applies default values within a schema

def validate( conf, schema ) :
  def defaults( validator_class ) :
    validate_properties = validator_class.VALIDATORS[ 'properties' ]
  
    def set_defaults( validator, properties, instance, schema ):
      for ( property, subschema ) in properties.items() :
        if ( 'default' in subschema ) :
          instance.setdefault( property, subschema[ 'default' ] )
  
      for error in validate_properties( validator, properties, instance, schema ):
        yield error

    return jsonschema.validators.extend( validator_class, { 'properties' : set_defaults } )

  validator = defaults( jsonschema.Draft6Validator ) ; validator( schema ).validate( conf )
