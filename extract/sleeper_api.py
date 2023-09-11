from sleeper_wrapper import League
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def map_rosterid_to_ownerid(rosters: list[dict]) -> dict:
    """
    This function is used to map the returned rosterid to ownerid

    :param rosters: list of dictionaries of roster data returned by League.get_rosters()
    :returns: dictionary of mapped rosterids -> ownerids for later use
    """

    result_dict = {}
    for roster in rosters:
        roster_id = roster["roster_id"]
        owner_id = roster["owner_id"]
        result_dict[roster_id] = owner_id

    return result_dict


def map_users_to_team_name(users: list[dict]) -> dict:
    """
    This function is used to map userids to their display name

    :param rosters: list of dictionaries of user data returned by League.get_users()
    :returns: dictionary of mapped userids -> display names for later use
    """

    users_dict = {}
    for user in users:
        users_dict[user["user_id"]] = user["display_name"]
    return users_dict


def get_weekly_data(
    rosters: list[dict],
    matchups: list[dict],
    users: list[dict],
    week: int,
    current_period: bool,
) -> pd.DataFrame:
    """
    This function is used to return weekly league data for each user

    :param rosters: list of dictionaries returned by League.get_rosters()
    :param matchups: list of dictionaries returned by League.get_matchups()
    :param users: list of dictionaries returned by League.get_users()
    :week: integer of week data being collected
    :current_period: bool flag to confirm if week is the current week or not

    :returns: DataFrame of all week data gathered
    """

    roster_id_dict = map_rosterid_to_ownerid(rosters)

    if len(matchups) == 0:
        return None

    # get the users to team name stats
    users_dict = map_users_to_team_name(users)

    # getting base scores
    scoreboards_dict = {}
    for team in matchups:
        # confirming matchups
        matchup_id = team["matchup_id"]
        current_roster_id = team["roster_id"]
        owner_id = roster_id_dict[current_roster_id]

        if owner_id is not None:
            user_name = users_dict[owner_id]
        else:
            user_name = "User name not available"
        # this is broken
        # team_score = self.get_team_score(team["starters"], score_type, week)
        # getting data of interest
        points_for = team["points"]
        if points_for is None:
            points_for = 0

        team_score_tuple = (owner_id, user_name, points_for)
        if matchup_id not in scoreboards_dict:
            scoreboards_dict[matchup_id] = [team_score_tuple]
        else:
            scoreboards_dict[matchup_id].append(team_score_tuple)

    # converting matchups to list for parsing
    data = []
    for _, value in scoreboards_dict.items():
        data.append(value[0] + value[1])
        data.append(value[1] + value[0])

    # generating team data
    final_team_data = []
    for team in data:
        team_data = {}
        team_data["user_id"] = str(team[0])
        team_data["user_name"] = team[1]
        team_data["week"] = week
        team_data["opponent_id"] = str(team[3])
        team_data["opponent_name"] = team[4]
        team_data["points_for"] = team[2]
        team_data["points_against"] = team[5]
        #team_data["points_spread"] = round(team[2] - team[5], 2)
        if week < 15:
            team_data["playoffs"] = False
        else:
            team_data["playoffs"] = True

        final_team_data.append(team_data)

    df = pd.DataFrame(final_team_data)

    # setting wins, losses, and ties
    # df["wins"] = np.where(df["points_for"] > df["points_against"], 1, 0)
    # df["losses"] = np.where(df["points_for"] < df["points_against"], 1, 0)
    # df["ties"] = np.where(df["points_for"] == df["points_against"], 1, 0)
    df["current_period"] = current_period
    df["points_spread"] = df["points_for"] - df["points_against"]

    return df


def get_roster_stats(rosters: list[dict]) -> pd.DataFrame:
    """
    This function is used to return relevant roster data to join to weekly
    matchup data

    :param rosters: roster data returned by League.get_rosters()
    :returns: DataFrame of relevant data for later use for each user in the league
    """

    # generating roster data
    roster_team_data = []
    for roster in rosters:
        roster_data = {}
        roster_data["user_id"] = str(roster["owner_id"])
        roster_data["waiver_budget_left"] = (
            100 - roster["settings"]["waiver_budget_used"]
        )
        roster_data["division"] = roster["settings"]["division"]
        roster_data["wins"] = roster["settings"]["wins"]
        roster_data["losses"] = roster["settings"]["losses"]
        roster_data["ties"] = roster["settings"]["ties"]

        try:
            roster_data["points_potential"] = float(
                str(roster["settings"]["ppts"])
                + "."
                + str(roster["settings"]["ppts_decimal"])
            )
            roster_data["win_streak"] = roster["metadata"]["streak"]
            roster_data["record"] = roster["metadata"]["record"]
        # really only needed to catch at start of season
        except KeyError:
            roster_data["points_potential"] = ""
            roster_data["win_streak"] = ""
            roster_data["record"] = ""

        roster_team_data.append(roster_data)

    df = pd.DataFrame(roster_team_data)
    df["current_period"] = True

    return df


def sleeper_data(league_id: str, weeks: dict, year: int) -> pd.DataFrame:
    """
    This is the main function that compiles all of the league
    data into a single DataFrame

    :param league_id: League ID as a string
    :param weeks: dictionary of weeks to target getting data from
    :param year: year for week data being targeted

    :returns: DataFrame of all week data for further processing

    """

    # establish league object and get data of interest
    league = League(league_id)
    users = league.get_users()
    rosters = league.get_rosters()

    all_weeks = []
    for key, value in weeks.items():
        # weekly matchup data
        matchups = league.get_matchups(key)
        # check if week has been completed or not
        if value[0]:
            logger.info(f"Gathering data for week {key} {year}")
            weekly_data = get_weekly_data(rosters, matchups, users, key, value[1])
            all_weeks.append(weekly_data)
            logger.info(f"Data successfully gathered for week {key} {year}")
        else:
            logger.warning(
                f"Week {key} {year} has not been played yet. Skipping getting this data"
            )

    all_week_data = pd.concat(all_weeks)

    # roster data
    roster_data = get_roster_stats(rosters)

    # merging data roster data for current period only
    final_data = all_week_data.merge(
        roster_data, how="left", on=["user_id", "current_period"]
    )

    # adding missing cols
    final_data["leauge_id"] = str(league_id)
    final_data["year"] = year

    return final_data
