import pandas as pd
import logging

from config.league_settings import *
from userargs.arguments import user_args
from extract.sleeper_api import sleeper_data
from upload.google_sheets import update_google_sheet

# getting logger
logger = logging.getLogger()


def main(
    league_info: list[tuple],
    sheet_name: str,
    file_name: str,
    current_week: int,
    current_year: int,
):
    """
    This is the main entry point function. It takes all config info and returns
    two CSVs for uploading to cloud to build dashboard tools

    :param league_info: list of tuples from config.league_settings
    :param sheet_name: name of Google worksheet to save data to
    :param file_name: file name from config.legaue_settings
    :param current_week: integer of week currently being run
    :param curent_year: integer of year currently being run

    :returns: Two CSVs for use in updating BI tool datasets

    """

    league_dataframes = []
    for league in league_info:
        # configuring weeks tuple = (completed week, current week)
        if league[1] != current_year:
            weeks = {}
            for i in range(1, 15):
                if i != 14:
                    weeks[i] = (True, False)
                else:
                    weeks[i] = (True, True)
        elif league[1] == current_year:
            weeks = {}
            for i in range(1, 15):
                # set current week
                if i == current_week:
                    weeks[i] = (True, True)
                # set uncompleted weeks to ignore
                elif i > current_week:
                    weeks[i] = (False, False)
                # set completed weeks
                else:
                    weeks[i] = (True, False)

        df = sleeper_data(league[0], weeks, league[1])
        league_dataframes.append(df)

    final_df = pd.concat(league_dataframes)

    # pivot for special power rankings
    pivot_data = pd.pivot_table(
        final_df[final_df["year"] == current_year],
        values="points_for",
        index="week",
        columns="user_name",
    )

    final_df.to_csv(file_name + ".csv", index=False)
    pivot_data.to_csv(file_name + "_pivot.csv")

    # fix data before uploading
    final_df = final_df.fillna(0)

    logger.info("Updating Google sheet with new data")
    # updating google sheets
    update_google_sheet(final_df, sheet_name)

    logger.info("Google sheet data updated successfully")


if __name__ == "__main__":
    # setting logging config
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    current_year, current_week = user_args()

    # work league
    logger.info("Generating new work league data files")
    main(work_league_info, work_google_sheet, work_file, current_week, current_year)
    logger.info("Work league data successfully updated")

    # friend leaguedata
    logger.info("Generating new friend league data files")
    main(
        friend_league_info, friend_google_sheet, friend_file, current_week, current_year
    )
    logger.info("Friend league data successfully updated")
