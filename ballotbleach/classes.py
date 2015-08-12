import csv
from ballotbleach import risk


DEFAULT_RISK_ASSESSMENTS = [risk.check_chain_stuffing, risk.check_verbosity,
                            risk.check_completion, risk.check_comment_duplication]


class Ballot(object):
    """
    Represents a vote submission.
    """
    def __init__(self, timestamp, council_rating=None, next_priorities=None,
                 most_effective='None'):
        self.id = None
        self._score_explanation = ''
        self.timestamp = timestamp
        self.council_rating = council_rating
        if not next_priorities:
            next_priorities = ''
        self.next_priorities = next_priorities
        self.most_effective = most_effective
        self.score = 0

    def __eq__(self, other):
        """
        Equal if an id is set and same value. The default id is None, so
        two ballots without properly set ids would not be matched as equal.
        """
        if self.id:
            return self.id == other.id
        else:
            return False

    def __str__(self):
        return 'Timestamp {0} - Rating {1} - Most Effective: {2}'.format(self.timestamp,
                                                                         self.council_rating,                                                                         self.most_efficient)
    @property
    def raw_priority(self):
        lowercase = self.next_priorities.lower()
        return lowercase.replace(" ", "").replace("-", "").strip()

    def update_score(self, amount=1):
        self.score = (self.score + amount)

    def add_explanation(self, explanation):
        if self._score_explanation:
            self._score_explanation = ''.join((self._score_explanation, '+', explanation,))
        else:
            self._score_explanation = explanation

    @property
    def explanation(self):
        if self._score_explanation:
            return self._score_explanation
        else:
            return ''


class Store(object):
    """
    A data store for ballots.

    Attributes:
        _store (list): A list of ballots. Not intended for direct access.
        _counter (int): The count of persisted ballots. Used to provide an
          identifier to ballots saved in the store.

    """
    def __init__(self, risk_assessments=None):
        self._store = []
        self._counter = 0
        if not risk_assessments:
            self.risk_assessments = DEFAULT_RISK_ASSESSMENTS

    def _increment_counter(self):
        self._counter += 1
        return self._counter

    def add_ballot(self, ballot):
        self._increment_counter()
        new_id = self._counter
        ballot.id = new_id
        self._store.append(ballot)

    def get_ballots(self):
        return self._store

    def print_all_ballots(self):
        for ballot in self._store:
            fields = str(ballot)
            print('Ballot {0} {1}'.format(ballot.id, fields))

    def to_csv(self, output_directory, output_file_name='ballots.csv', cutoff_score=None):
        """
        Creates a CSV file with each ballot in the Store represented by a row of data.
        """
        output_csv = ''.join((output_directory, output_file_name))
        with open(output_csv, 'w', newline='') as csv_file:
            ballot_writer = csv.writer(csv_file)
            ballots = self.get_ballots()
            rows = []
            for ballot in ballots:
                if cutoff_score is None or ballot.score < cutoff_score:
                    row = [ballot.id, ballot.timestamp, ballot.council_rating,
                           ballot.most_effective, ballot.raw_priority,
                           ballot.score, ballot.explanation]
                    rows.append(row)
            ballot_writer.writerows(rows)

    def score_risk(self):
        for assessment in self.risk_assessments:
            assessment(self.get_ballots())
