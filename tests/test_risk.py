from datetime import datetime
import unittest
from ballotbleach import classes
from ballotbleach import risk


class TestStore(classes.Store):

    def __init__(self, risk_assessments=None):
        super(TestStore, self).__init__(risk_assessments=risk_assessments)
        # id: 1
        self.add_ballot(classes.Ballot(datetime.now(), 10, 'Housing, transportation, cops, taxes', 'Washington'))
        self.add_ballot(classes.Ballot(datetime.now(), 9, 'Policing, noise, sidewalks, taxes', 'Lincoln'))
        self.add_ballot(classes.Ballot(datetime.now(), 8, 'Trees, water, sidewalks', 'Polk'))
        self.add_ballot(classes.Ballot(datetime.now(), 8, 'Trees, water, sidewalks', 'Polk'))
        # id: 5
        self.add_ballot(classes.Ballot(datetime.now(), 6, 'Affordability', 'Roosevelt'))
        self.add_ballot(classes.Ballot(datetime.now(), 5, 'Affordability', 'Roosevelt'))
        self.add_ballot(classes.Ballot(datetime.now(), 5, 'Growth with shared prosperity', 'Johnson'))
        self.add_ballot(classes.Ballot(datetime.now(), 3, '', 'Obama'))
        self.add_ballot(classes.Ballot(datetime.now(), None, 'Planning and policy initiatives', 'Johnson'))
        # id: 10
        self.add_ballot(classes.Ballot(datetime.now(), None, '1. An item 2. Another item 3. Thing', 'Obama'))
        self.add_ballot(classes.Ballot(datetime.now(), None, '', 'Obama'))


class CheckChainStuffingTests(unittest.TestCase):

    def setUp(self):
        self.store = TestStore()

    def test_chain_stuffing(self):
        ballots = self.store.get_ballots()
        risk.check_chain_stuffing(ballots)
        results = {}
        for ballot in ballots:
            results[str(ballot.id)] = ballot.score
        self.assertEquals(results['1'], 0)
        self.assertEquals(results['2'], 0)
        self.assertEquals(results['3'], 0)
        self.assertEquals(results['4'], 0)
        self.assertEquals(results['5'], 0)
        self.assertEquals(results['6'], 0)
        self.assertEquals(results['7'], 0)
        self.assertEquals(results['8'], 0)
        self.assertEquals(results['9'], 0)
        self.assertEquals(results['10'], 20)
        self.assertEquals(results['11'], 0)


class CheckVerbosityTests(unittest.TestCase):

    def setUp(self):
        self.store = TestStore()

    def test_verbosity(self):
        ballots = self.store.get_ballots()
        risk.check_verbosity(ballots)
        results = {}
        for ballot in ballots:
            results[str(ballot.id)] = ballot.score
        self.assertEquals(results['1'], 0)
        self.assertEquals(results['2'], 0)
        self.assertEquals(results['3'], 25)
        self.assertEquals(results['4'], 25)
        self.assertEquals(results['5'], 25)
        self.assertEquals(results['6'], 25)
        self.assertEquals(results['7'], 0)
        self.assertEquals(results['8'], 25)
        self.assertEquals(results['9'], 0)
        self.assertEquals(results['10'], 0)
        self.assertEquals(results['11'], 25)


class CheckCompletionTests(unittest.TestCase):

    def setUp(self):
        self.store = TestStore()

    def test_completion_scoring(self):
        ballots = self.store.get_ballots()
        risk.check_completion(ballots)
        results = {}
        for ballot in ballots:
            results[str(ballot.id)] = ballot.score
        self.assertEquals(results['1'], 0)
        self.assertEquals(results['2'], 0)
        self.assertEquals(results['3'], 0)
        self.assertEquals(results['4'], 0)
        self.assertEquals(results['5'], 0)
        self.assertEquals(results['6'], 0)
        self.assertEquals(results['7'], 0)
        self.assertEquals(results['8'], 50)
        self.assertEquals(results['9'], 50)
        self.assertEquals(results['10'], 50)
        self.assertEquals(results['11'], 100)

    def test_completion_explanation(self):
        ballots = self.store.get_ballots()
        risk.check_completion(ballots)
        results = {}
        for ballot in ballots:
            results[str(ballot.id)] = ballot.explanation
        self.assertEquals(results['1'], '')
        self.assertEquals(results['2'], '')
        self.assertEquals(results['3'], '')
        self.assertEquals(results['4'], '')
        self.assertEquals(results['5'], '')
        self.assertEquals(results['6'], '')
        self.assertEquals(results['7'], '')
        self.assertEquals(results['8'], 'incomplete-feedback')
        self.assertEquals(results['9'], 'incomplete-rating')
        self.assertEquals(results['10'], 'incomplete-rating')
        self.assertEquals(results['11'], 'incomplete-rating+incomplete-feedback')


class CheckCommentDuplicationTests(unittest.TestCase):

    def setUp(self):
        self.store = TestStore()

    def test_duplication(self):
        ballots = self.store.get_ballots()
        risk.check_comment_duplication(ballots)
        results = {}
        for ballot in ballots:
            results[str(ballot.id)] = ballot.score
        self.assertTrue(results['1'] == 0)
        self.assertTrue(results['2'] == 0)
        self.assertTrue(results['3'] == 0)
        self.assertTrue(results['4'] == 75)
        self.assertTrue(results['5'] == 0)
        self.assertTrue(results['6'] == 75)
        self.assertTrue(results['7'] == 0)
        self.assertTrue(results['8'] == 0)
        self.assertTrue(results['9'] == 0)
        self.assertTrue(results['10'] == 0)
