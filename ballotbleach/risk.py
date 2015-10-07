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
    Checks for ballots with the same 'selected_actor' answer and empty
    'feedback'.  Returns True if the size of the matching batch
    exceeds the qualifying length argument.
    """
    sibling_batch = []
    selected_actor = ballot.selected_actor
    if selected_actor:
        for comparison_ballot in comparison_ballots:
            if selected_actor == comparison_ballot.selected_actor \
                    and len(comparison_ballot.feedback) == 0:
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
            risk_increment = 100 if len(ballot.raw_feedback) == 0 else 20
        if risk_increment > 0:
            ballot.update_score(risk_increment)
            ballot.add_explanation('chain')


def check_verbosity(ballots):
    """
    Increases risk score if a ballot has feedback that
    is three words or less.
    """
    for ballot in ballots:
        if ballot.raw_feedback:
            word_count = len(re.findall(r'[\w]+', ballot.feedback))
            if word_count > 3:
                continue
        ballot.update_score(25)
        ballot.add_explanation('short-feedback')



def check_completion(ballots):
    """
    Increases risk score if a ballot is missing either the subject rating
    or feedback.
    """
    for ballot in ballots:
        if not ballot.subject_rating:
            ballot.update_score(50)
            ballot.add_explanation('incomplete-rating')
        if not ballot.raw_feedback:
            ballot.update_score(50)
            ballot.add_explanation('incomplete-feedback')


def check_comment_duplication(ballots):
    """
    Increases risk score if a ballot's feedback matches the
    content of a different ballot submitted at a later point for the same selected actor.
    """
    for ballot in ballots:
        if ballot.raw_feedback:
            other_ballots = get_comparison_ballots(ballot, ballots)
            for comparison_ballot in other_ballots:
                if ballot.raw_feedback == comparison_ballot.raw_feedback \
                        and ballot.selected_actor == comparison_ballot.selected_actor \
                        and ballot.timestamp > comparison_ballot.timestamp:
                    ballot.update_score(75)
                    ballot.add_explanation('duplicate')
                    break


