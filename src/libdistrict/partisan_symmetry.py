import statistics
from libdistrict.district import District


def efficiency_gap(district_plan, party_a, party_b):
    """
    :param district_plan: an iterable of Districts
    :param party_a: key value / name of party a (Democratic by convention - positive scores denote pro-Democratic asymmetries)
    :param party_b: key value / name of party b (Republican by convention - negative scores denote pro-Republican asymmetries)
    :return: the efficiency gap (positive for party a, negative for party b)
    """

    is_district_plan(district_plan)

    party_a_wasted = 0
    party_b_wasted = 0
    total_votes = 0

    for district in district_plan:
        party_a_votes = district.party_votes[party_a]
        party_b_votes = district.party_votes[party_b]
        total_votes += (party_a_votes + party_b_votes)
        win_threshold = (party_a_votes + party_b_votes) / 2

        if party_a_votes > party_b_votes:
            party_a_wasted += (party_a_votes - win_threshold)
            party_b_wasted += party_b_votes
        elif party_a_votes < party_b_votes:
            party_a_wasted += party_a_votes
            party_b_wasted += (party_b_votes - win_threshold)
        else:
            pass

    return (party_b_wasted - party_a_wasted) / total_votes



def mean_median_diff(district_plan, party_to_analyze, competing_party):
    """
    :param district_plan: an iterable of Districts
    :param party_to_analyze: the key specifying which party to analyze
    :param competing_party: the competing party
    :return: median - mean party share across all districts
    a small difference indicates a more symmetric district distribution,
        while a large difference indicates that district distribution is skewed
        in favor of one party and against its opponent
    a negative score means the analyzed party may have a disadvantage
    a positive score means the analyzed party may have an advantage
    """

    is_district_plan(district_plan)

    vote_share_per_district = []

    # store all votes for party in a sequence
    for district in district_plan:
        vote_share_per_district.append(partisan_index(district, party_to_analyze, competing_party))

    # get the median votes for all districts for the party
    party_share_median = statistics.median(vote_share_per_district)

    # get the mean for all districts for the party
    party_share_mean = statistics.mean(vote_share_per_district)

    return party_share_median - party_share_mean

def competitiveness(district_plan, party_a, party_b, range):
    """
    :param district_plan: an iterable of Districts
    :param party_a: key value / name of party a (Democratic by convention)
    :param party_b: key value / name of party b (Republican by convention)
    :param range: range from 0.5
    :return: number of "fair" districts -
        districts with a partisan index that falls within the desired range
    """

    is_district_plan(district_plan)

    low = 0.5 - range
    high = 0.5 + range
    num_fair = 0

    for district in district_plan:
        p_index = partisan_index(district, party_a, party_b)
        if low < p_index < high:
            num_fair += 1

    return num_fair

# Helper Methods for Partisan Symmetry Functions
def is_district(district):
    if not isinstance(district, District):
        raise TypeError

def is_district_plan(district_plan):
    if district_plan is None:
        raise TypeError
    for district in district_plan:
        is_district(district)

def partisan_index(district, party_to_analyze, competing_party):

    is_district(district)

    return (district.party_votes[party_to_analyze] / 
            (district.party_votes[party_to_analyze] + district.party_votes[competing_party]))