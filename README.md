# Sleeper Stats

This package is used to pull in data from various Sleeper fantasy football leagues and extract data to CSV and Google Sheets for use in downstream Looker Studio reporting. The main module of the package uses `sleeper-api-wrapper` to interact with the Sleeper API and adds additional functions used to parse the returned data into the format required for Looker Studio. 

Package dependencies can be found in the `requirements.txt` file.

**Table of Contents**
- [Sleeper Stats](#sleeper-stats)
- [Package info](#package-info)
  - [config](#config)
  - [extract](#extract)
  - [output](#output)
  - [tests](#tests)
  - [upload](#upload)
  - [userargs](#userargs)
- [How to setup Google Sheets API](#how-to-setup-google-sheets-api)
- [How to run script](#how-to-run-script)


# Package info
See below for information regarding the folders contained in this package

## config
This folder contains the module `league_settings.py`. In this module, you will need to update the variables below with your specified league info to be able to run the script:

>Tip: Variable names can be amended as needed. At a bare minimum, you will need these variables to run the script:
* `friend_league_info`
  * This is a `list` of `tuples` in this format: `[(league_id, year)]`
* `friend_file` = output file name
* `friend_google_sheet` = name of Google sheet

## extract
This folder contains the module `sleeper_api.py`. This module contains all of the necessary functions to return and parse the data from the Sleeper API.

The base of the function `sleeper_data()` relies on the Class `League()` from `sleeper_wrapper` package that is used to parse the data from the API into Python objects.The rest of the functions are custom to parse the data into the format required by downstream BI reporting.

## output
This folder is where any output CSV files will be sent to

## tests
This folder contains test files used to work with the Sleeper API in case anything changes in the future. 

## upload
This folder contains the module `google_sheets.py` that is used to work with Google Sheets. The base of this module is based on the `gspread` package. 

>Tip: Please make sure you setup a Google Cloud project and Service Account before trying to run the main script per the how to below.

## userargs
This folder contains the module `arguments.py` that is used to parse the required command line arguments.

Required command line arguments are:
* `--year`
  * This is the current year of the report being run in integer format (i.e. 2022, 2023, etc)
* `--week`
  * This is the current week of the report being run in integer format (i.e. 1, 2, 3, 4, 5, etc)

# How to setup Google Sheets API
Check out this [link](https://aryanirani123.medium.com/read-and-write-data-in-google-sheets-using-python-and-the-google-sheets-api-6e206a242f20) for step by step instructions for setting up a new Google Cloud Project and running the Google Sheets API with it.

# How to run script
1. Ensure you have setup the Google Cloud Project, Google Sheets API, and Service account per the steps above
2. Configure your Google Sheet targets and update the `league_settings.py` with your league information
   1. If only running for one league, update the `main()` call in `sleeper_stats.py` to only run for the specified league
3. Once everything is configured, open a terminal and navigate to where this package is stored on your machine.
4. Next, run the command `python -u sleeper_stats.py --year {input year} --week {input week}` and hit enter
5. The script will pull the requested data from Sleeper API, parse it, and send to CSV and Google Sheets target(s) as required.
6. Repeat steps above as needed to refresh your data. 
> Tip: All weeks set before command --week will be run automatically. Therefore, if you are running for say week 5, then data for weeks 1-4 will also be pulled and updated. 

> Tip: If you need to pull data for an entire year, then specify the old league ID and year in the config and set the --year param to the current year. This will then ensure the entire week data for the prior year is pulled and updated at runtime.