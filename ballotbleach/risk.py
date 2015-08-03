import re


BALLOT_TIME_CUTOFF = 0


def has_submission_overlap(origin_ballot, target_ballot, time_cutoff):
    pass


def check_chain_stuffing(ballots):
    """
    Increases the risk score for a ballot if it is part of a
    pattern of similar ballots submitted in a unusually short
    amount of time.
    """
    for ballot in ballots:
        other_ballots = list(ballots)
        other_ballots.remove(ballot)
        for target_ballot in other_ballots:
            if has_submission_overlap(ballot, target_ballot, BALLOT_TIME_CUTOFF):
                ballot.update_score(3)
                ballot.score_explanation += '+chain'



def check_verbosity(ballots):
    """
    Increases risk score if a ballot has a priorities comment that
    is less than three words.
    """
    for ballot in ballots:
        word_count = len(re.findall(r'[\w]+', ballot.next_priorities))
        if word_count < 3:
            ballot.update_score(1)
            ballot.score_explanation += '+short'


def check_completion(ballots):
    """
    Increases risk score if a ballot is missing both the Council Member
    and satisfaction score.
    """
    for ballot in ballots:
        if not ballot.council_rating or not ballot.next_priorities:
            ballot.update_score(2)
            ballot.score_explanation += '+incomplete'


def check_comment_duplication(ballots):
    """
    Increases risk score if a ballot's priorities comment matches the
    content of a different ballot.
    """
    for ballot in ballots:
        other_ballots = list(ballots)
        other_ballots.remove(ballot)
        for comparison_ballot in other_ballots:
            if ballot.raw_prioritiy == comparison_ballot.raw_priority:
                ballot.update_score(2)
                ballot.score_explanation += '+duplicate-priorities'


