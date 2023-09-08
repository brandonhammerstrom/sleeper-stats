import gspread
import pandas as pd


def update_google_sheet(df: pd.DataFrame, sheet_name: str):
    gc = gspread.service_account()

    sh = gc.open(sheet_name)

    worksheet = sh.sheet1

    worksheet.clear()

    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
