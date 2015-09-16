"""
Ballot and Store classes.

Attributes:
    DEFAULT_RISK_ASSESSMENTS (list): The default list of risk assessment functions.
"""
import csv
from ballotbleach import risk


DEFAULT_RISK_ASSESSMENTS = [risk.check_chain_stuffing, risk.check_verbosity,
                            risk.check_completion, risk.check_comment_duplication]


class Ballot(object):
    """
    Represents a vote submission for a survey that is compliant with the Civic Leadership Assessment specifcation.
    """
    def __init__(self, timestamp, subject_rating=None, feedback=None,
                 selected_actor='None'):
        self.id = None
        self._score_explanation = ''
        self.timestamp = timestamp
        self.subject_rating = subject_rating
        if not feedback:
            feedback = ''
        self.feedback = feedback
        self.selected_actor = selected_actor
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
        return 'Timestamp {0} - Rating {1} - Selected Actor: {2}'.format(self.timestamp,
                                                                         self.subject_rating,
                                                                         self.selected_actor)
    @property
    def raw_feedback(self):
        """
        Returns the feedback content without white space or hyphens, in all lowercase characters.
        This simplifies analysis such as word counts and word cloud generation.
        """
        lowercase = self.feedback.lower()
        return lowercase.replace(" ", "").replace("-", "").strip()

    def update_score(self, amount=1):
        """
        Add the passed amount to the existing risk score.
        """
        self.score = (self.score + amount)

    def add_explanation(self, explanation):
        """
        Add the passed explanatory detail to the ballot's risk score explanation.
        """
        if self._score_explanation:
            self._score_explanation = ''.join((self._score_explanation, '+', explanation,))
        else:
            self._score_explanation = explanation

    @property
    def explanation(self):
        """
        Returns the ballot's risk score explanation.
        """
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
        risk_assessments (list): A list of risk assessment functions that are run on ballots.
            If no assessments are passed during initialization,
            it utilizes :data:`~ballotbleach.classes.DEFAULT_RISK_ASSESSMENTS`.

    """
    def __init__(self, risk_assessments=None):
        self._store = list()
        self._counter = 0
        if not risk_assessments:
            self.risk_assessments = DEFAULT_RISK_ASSESSMENTS

    def _increment_counter(self):
        self._counter += 1
        return self._counter

    def add_ballot(self, ballot):
        """
        Adds a ballot model to the store while providing it a unique integer identifier as its 'id' property.
        """
        self._increment_counter()
        new_id = self._counter
        ballot.id = new_id
        self._store.append(ballot)

    def get_ballots(self):
        """
        Returns the store's list of ballots.  Will return an empty list if no ballots stored.
        """
        return self._store

    def print_all_ballots(self):
        """
        Prints basic info about each ballot in store on command line.
        """
        for ballot in self._store:
            fields = str(ballot)
            print('Ballot {0} {1}'.format(ballot.id, fields))

    def filter_ballots(self, cutoff_score):
        """
        Returns ballots under the cutoff score.  If not cutoff score is passed, then all ballots are returned.
        """
        cleared_ballots = list()
        for candidate_ballot in self.get_ballots():
            if cutoff_score is None or candidate_ballot.score < cutoff_score:
                cleared_ballots.append(candidate_ballot)
        return cleared_ballots

    def get_rows(self, cutoff_score):
        """
        Returns ballots under the cutoff score in a *row* format that is compatible with CSV-writing. If not cutoff
        is passed, then all ballots are returned.
        """
        rows = list()
        for ballot in self.get_ballots():
            if cutoff_score is None or ballot.score < cutoff_score:
                row = [ballot.id, ballot.timestamp, ballot.subject_rating,
                       ballot.selected_actor, ballot.raw_feedback,
                       ballot.score, ballot.explanation]
                rows.append(row)
        return rows

    def to_csv(self, output_directory, output_file_name='ballots.csv', cutoff_score=None):
        """
        Creates a CSV file with each ballot in the Store represented by a row of data.
        """
        output_csv = ''.join((output_directory, output_file_name))
        with open(output_csv, 'w', newline='') as csv_file:
            ballot_writer = csv.writer(csv_file)
            ballot_writer.writerows(self.get_rows(cutoff_score))

    def score_risk(self):
        for assessment in self.risk_assessments:
            assessment(self.get_ballots())
