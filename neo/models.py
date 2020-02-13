# from django.db import models

# Create your models here.
from neomodel import (config, StructuredNode, StringProperty, IntegerProperty,
    UniqueIdProperty, RelationshipTo,ArrayProperty,BooleanProperty)
config.DATABASE_URL = 'bolt://neo4j:9848022338@3.8.5.0:7687'


class Symptom(StructuredNode):
#     name = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    ar_name = StringProperty()
    description = StringProperty()
    ar_description = StringProperty()
    synonyms = ArrayProperty()
    ar_synonyns = ArrayProperty()

    # traverse outgoing IS_FROM relations, inflate to Country objects
    
class Disease(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    ar_name = StringProperty()
    description = StringProperty()
    ar_description = StringProperty()
    has = RelationshipTo(Symptom, 'has') 
    
    
class Doctor(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    ar_name = StringProperty()
    description = StringProperty()
    ar_description = StringProperty()
    covers = RelationshipTo(Disease, 'covers') 
    
class User(StructuredNode):
    name= StringProperty()
    gender= StringProperty()
    pregnancy= BooleanProperty()
    group= StringProperty()
    might_have = RelationshipTo(Symptom, 'might_have')
    
