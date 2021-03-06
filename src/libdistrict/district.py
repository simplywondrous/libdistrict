"""@package docstring
District class contains district information.

This class is a parameter to all the metric fucntions, 
either individually or a part of the district plans. 
"""

class District:

    def __init__(self, id=None, population=None, votes=None, party_votes=None, geometry=None):
        """
        :param id: the unique identifier for this district
        :param population: population of this district
        :param votes: all votes in this district for the election
        :param party_votes: dictionary whose keys are strings (party) and values (votes)
        :param geometry: spatial geometry of this district
        """
        self.id = id
        self.population = population
        self.votes = votes
        self.party_votes = party_votes
        self.geometry = geometry
