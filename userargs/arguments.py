import argparse


def user_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help=f"""Please type current year as integer. Start date for leagues is 2022 and beyond""",
    )
    parser.add_argument(
        "--week",
        type=int,
        choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
        required=True,
        help=f"""Please type current week as integer. Only weeks 1-14 are supported""",
    )
    args = parser.parse_args()

    return args.year, args.week
