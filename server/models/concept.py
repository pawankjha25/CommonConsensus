from google.appengine.ext import ndb
from google.appengine.api import memcache
import logging
import datetime
import random
from collections import defaultdict

class Concept(ndb.Model):
    """
    A word/phrase representative of a concept
    """
    name = ndb.StringProperty()
    concept_types = ndb.StringProperty(repeated=True)
    created_at = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def get_concept_types(cls):
        """
        Returns all of the concept tags
        """
        concept_types = set()
        for concept in ndb.gql("SELECT concept_types FROM Concept").fetch():
            for ct in concept.concept_types:
                concept_types.add(ct)
        return concept_types

    @classmethod
    def get_random(cls, concept_type):
        """
        Returns a random concept of a particular type
        """
        concepts = cls.query(cls.concept_types==concept_type).fetch()
        if len(concepts) == 0:
            msg = "ConceptType %s has no members" % (concept_type)
            logging.error(msg)
            raise GameCreationException(msg)
        return concepts[random.randint(0, len(concepts)-1)]


    def add_concept_type(self, concept_type):
        """
        Adds a concept type
        """
        cleaned = concept_type.strip().lower()
        if cleaned not in self.concept_types:
            self.concept_types.append(cleaned)


class Predicate(ndb.Model):
    """
    Contains all of the predicates
    """
    predicate = ndb.StringProperty(required=True)
    arguments = ndb.StringProperty(repeated=True)
    argument_types = ndb.StringProperty(repeated=True)
    frequency = ndb.IntegerProperty(default=0)

    @classmethod
    def update_or_create(cls, predicate, arguments, argument_types, frequency=1):
        """
        Gets the predicate or adds to the existing one
        """
        logging.info("PREDICATE\n"+str(predicate))
        logging.info("ARGUMENTS\n"+str(arguments))
        p = ndb.gql("""SELECT * FROM Predicate
                         WHERE predicate = :1
                         AND argument_types IN :2
                         AND arguments IN :3""", predicate, argument_types, arguments).get()
        if not p:
            p = cls(predicate=predicate,
                    arguments=arguments,
                    argument_types=argument_types)

        p.frequency += frequency
        return p
        

    def fancy_form(self):
        """
        Typed predicate string format
        """
        arg_types = ["%s:%s" % (p[0],p[1]) \
                for p in zip(self.arguments, self.argument_types)]
        return "%s(%s)" % (self.predicate, ', '.join(arg_types))
