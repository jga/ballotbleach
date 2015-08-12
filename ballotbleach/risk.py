from datetime import datetime, timedelta
import re

# In seconds. So, 420 is 7 minutes.
BALLOT_TIME_CUTOFF = 420


def is_near(timestamp, start, stop):
    if start <= timestamp <= stop:
        return True
    else:
        return False


def get_near_cutoffs(base, cutoff):
    """
    Returns a "start" and a "stop" datetime calculated by
    subtracting and adding a quantity of time (timedelta) to a baseline
    moment.

    Arguments:
        base (datetime): The baseline datetime moment from which
        cutoffs will be calculated.
        cutoff (integer): The interval to be added and subtracted in seconds.
    """
    delta = timedelta(seconds=cutoff)
    start = base - delta
    stop = base + delta
    return start, stop


def get_comparison_ballots(ballot, ballots):
    other_ballots = list(ballots)
    other_ballots.remove(ballot)
    return other_ballots


def get_near_ballots(ballot, ballots, cutoff):
    """
    Returns a list of comparison ballots that were created within a
    specified time interval before and after the creation of a "baseline" ballot
    """
    near_ballots = []
    other_ballots = list(ballots)
    other_ballots.remove(ballot)
    start, stop = get_near_cutoffs(ballot.timestamp, cutoff)
    for other_ballot in other_ballots:
        if is_near(other_ballot.timestamp, start, stop):
            near_ballots.append(other_ballot)
    return near_ballots


def has_empty_sibling_batch(ballot, comparison_ballots, qualifying_length=2):
    """
    Checks for ballots with the same 'most_effective' answer and empty
    'next_priorities'.  Returns True if the size of the matching batch
    exceeds the qualifying length argument.
    """
    sibling_batch = []
    most_effective = ballot.most_effective
    if most_effective:
        for comparison_ballot in comparison_ballots:
            if most_effective == comparison_ballot.most_effective \
                    and len(comparison_ballot.raw_priority) == 0:
                sibling_batch.append(comparison_ballot)
    if len(sibling_batch) >= qualifying_length:
        return True
    else:
        return False


def check_chain_stuffing(ballots):
    """
    Increases the risk score for a ballot if it is member of a
    pattern of similar ballots submitted in a suspiciously short
    amount of time.
    """
    for ballot in ballots:
        risk_increment = 0
        near_ballots = get_near_ballots(ballot, ballots, BALLOT_TIME_CUTOFF)
        if has_empty_sibling_batch(ballot, near_ballots):
            risk_increment = 100 if len(ballot.raw_priority) == 0 else 20
        if risk_increment > 0:
            ballot.update_score(risk_increment)
            ballot.add_explanation('chain')


def check_verbosity(ballots):
    """
    Increases risk score if a ballot has a priorities comment that
    is less than three words.
    """
    for ballot in ballots:
        if ballot.raw_priority:
            word_count = len(re.findall(r'[\w]+', ballot.next_priorities))
            if word_count < 3:
                ballot.update_score(25)
                ballot.add_explanation('short')


def check_completion(ballots):
    """
    Increases risk score if a ballot is missing either the Council Member
    or satisfaction score.
    """
    for ballot in ballots:
        if not ballot.council_rating:
            ballot.update_score(50)
            ballot.add_explanation('incomplete-rating')
        if not ballot.raw_priority:
            ballot.update_score(50)
            ballot.add_explanation('incomplete-priorities')


def check_comment_duplication(ballots):
    """
    Increases risk score if a ballot's priorities comment matches the
    content of a different ballot.
    """
    for ballot in ballots:
        if ballot.raw_priority:
            other_ballots = get_comparison_ballots(ballot, ballots)
            for comparison_ballot in other_ballots:
                if ballot.raw_priority == comparison_ballot.raw_priority \
                        and ballot.most_effective == comparison_ballot.most_effective \
                        and ballot.timestamp > comparison_ballot.timestamp:
                    ballot.update_score(75)
                    ballot.add_explanation('duplicate')
                    break


