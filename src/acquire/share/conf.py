# Copyright (C) 2018 SCARV project <info@scarv.org>
#
# Use of this source code is restricted per the MIT license, a copy of which 
# can be found at https://opensource.org/licenses/MIT (or should be included 
# as LICENSE.txt within the associated archive or repository).

from acquire import share

import json, jsonschema, os, sys

class Conf( dict ) :
  def __init__( self, conf = None ) :
    super().__init__()

    if ( conf != None ) :
      self.populate( conf )

  def has( self, key,        section = None               ) :
    if ( section != None ) :
      key = section + ':' + key

    return ( key in self )

  def get( self, key,        section = None, value = None ) :
    if ( section != None ) :
      key = section + ':' + key
  
    return self[ key ] if ( key in self ) else value
  
  def put( self, key, value, section = None               ) :
    if ( section != None ) :
      key = section + ':' + key
  
    self[ key ] = value

  def keys( self, section = None ) :
    r = list()

    for key in super().keys() :
      if ( ( section == None ) or ( key.startswith( section + ':' ) ) ) :
        r.append( key )

    return r

  def populate( self, x ) :
    if   ( isinstance( x, dict ) ) :
                              self.update(             x    )
    elif ( isinstance( x, str  ) ) :
      if ( os.path.isfile( x ) ) :
        fd = open( x, 'r' ) ; self.update( json.load ( fd ) ) ; fd.close()
      else :
                              self.update( json.loads( x  ) )

    for ( key, value ) in self.items() :
      if ( value != None ) :
        if   ( isinstance( value, dict ) ) :
          value = share.conf.Conf( conf = value )
        elif ( isinstance( value, str  ) ) :
          value = os.path.expandvars( value )

      self[ key ] = value

def extend_with_default( validator_class ) :
  validate_properties = validator_class.VALIDATORS[ 'properties' ]

  def set_defaults(validator, properties, instance, schema):
    for ( property, subschema ) in properties.items() :
      if 'default' in subschema :
        instance.setdefault( property, subschema[ 'default' ] )

    for error in validate_properties( validator, properties, instance, schema ):
      yield error

  return jsonschema.validators.extend( validator_class, { 'properties' : set_defaults } )

validator = extend_with_default( jsonschema.Draft4Validator )

def validate( conf, schema ) :
  validator( schema ).validate( conf )
