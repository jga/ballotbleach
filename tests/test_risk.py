from datetime import datetime
import unittest
from ballotbleach import classes
from ballotbleach import risk


class TestStore(classes.Store):

    def __init__(self, risk_assessments=None):
        super(TestStore, self).__init__(risk_assessments=risk_assessments)
        self.add_ballot(classes.Ballot(datetime.now(), 10, 'Housing, transportation, taxes', 'Washington'))
        self.add_ballot(classes.Ballot(datetime.now(), 9, 'Policing, noise, taxes', 'Lincoln'))
        self.add_ballot(classes.Ballot(datetime.now(), 8, 'Trees, water, sidewalks', 'Polk'))
        self.add_ballot(classes.Ballot(datetime.now(), 8, 'Trees, water, sidewalks', 'Polk'))
        self.add_ballot(classes.Ballot(datetime.now(), 6, 'Affordability', 'Roosevelt'))
        self.add_ballot(classes.Ballot(datetime.now(), 5, 'Affordability', 'Roosevelt'))
        self.add_ballot(classes.Ballot(datetime.now(), 5, 'Growth', 'Johnson'))
        self.add_ballot(classes.Ballot(datetime.now(), 3, '', 'Johnson'))
        self.add_ballot(classes.Ballot(datetime.now(), 1, 'Planning and policy', 'Johnson'))
        self.add_ballot(classes.Ballot(datetime.now(), 1, 'Gentrification', 'Obama'))


class CheckChainStuffingTests(unittest.TestCase):

    def setUp(self):
        self.store = TestStore()


class CheckVerbosityTests(unittest.TestCase):

    def setUp(self):
        self.store = TestStore()


class CheckCompletionTests(unittest.TestCase):

    def setUp(self):
        self.store = TestStore()


class CheckCommentDuplicationTests(unittest.TestCase):

    def setUp(self):
        self.store = TestStore()
