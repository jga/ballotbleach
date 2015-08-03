
class Ballot(object):
    """
    Represents a vote submission.
    """
    def __init__(self, timestamp, council_rating=None, next_priorities=None,
                 most_efficient='None of the above'):
        self.timestamp = timestamp
        self.council_rating = council_rating
        self.next_priorities = next_priorities
        self.most_efficient = most_efficient
        self.score = 0

    def __str__(self):
        return 'Timestamp {0} - Rating {1} - Most Effective: {2}'.format(self.timestamp,
                                                                         self.council_rating,
                                                                         self.most_efficient)

    def update_score(self, amount=1):
        self.score = (self.score + amount)


class Store(object):
    """
    A data store for ballots.

    Attributes:
        _store (list): A list of ballots. Not intended for direct access.
        _counter (int): The count of persisted ballots. Used to provide an
          identifier to ballots saved in the store.

    """
    def __init__(self):
        self._store = []
        self._counter = 0

    def _increment_counter(self):
        self._counter += 1
        return self._counter

    def add_ballot(self, ballot):
        self._increment_counter()
        new_id = self._counter
        ballot.id = new_id
        self._store.append(ballot)

    def print_all_ballots(self):
        for ballot in self._store:
            fields = str(ballot)
            print('Ballot {0} {1}'.format(ballot.id, fields))

    def to_csv(self, file_path, cutoff_score, output_name='ballots'):
        pass