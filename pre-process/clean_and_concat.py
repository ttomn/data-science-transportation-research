import numpy as np
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point
import warnings

warnings.filterwarnings("ignore")

DIR_PATH_TOM = "C:\\Users\\ttomn\\OneDrive\\Desktop\\data-science-transportation-research"
DIR_PATH_MAX = "C:\\Users\\maxba\\Desktop\\Study\\Third Year\\Final Project\\data-science-transportation-research"

SUMMONS_FILE = "with_streets_not_na_NYPD_B_Summons__Year_to_Date_.csv"
OLD_SUMMONS_FILE = "with_streets_not_na_NYPD_B_Summons__Historic_.csv"
COLLISIONS_FILE = "with_streets_not_na_Motor_Vehicle_Collisions_-_Crashes.csv"
FILES_NAMES_TO_EXECUTE = [SUMMONS_FILE, OLD_SUMMONS_FILE, COLLISIONS_FILE]
COLS_TO_TAKE_FROM_SUMMONS = ["VIOLATION_DATE", "VIOLATION_TIME", "VIOLATION_CODE", "VEH_CATEGORY",
                             "STREET", "ST_INDEX"]

weekday_mapping = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
}


def unit_summons():
    summons_df = pd.read_csv(f"{DIR_PATH_TOM}\\{SUMMONS_FILE}")
    old_summons_df = pd.read_csv(f"{DIR_PATH_TOM}\\{OLD_SUMMONS_FILE}")
    summons_df = create_summons_cols(summons_df)
    old_summons_df = create_summons_cols(old_summons_df)
    all_summons = pd.concat([summons_df, old_summons_df], axis=0)
    all_summons.to_csv("DIR_PATH_TOM}\\united_summons.csv")


def create_summons_cols(df):
    df = df[COLS_TO_TAKE_FROM_SUMMONS]
    df = get_timing_cols(df, date_col_name="VIOLATION_DATE", time_col_name="VIOLATION_TIME")
    return df


def get_timing_cols(df, date_col_name, time_col_name):
    date = pd.DatetimeIndex(df[date_col_name])
    time = pd.DatetimeIndex(df[time_col_name])
    df['MONTH'] = date.month
    df['YEAR'] = date.year
    df['DAY'] = date.day
    df['DAY_OF_WEEK'] = date.day_name().map(weekday_mapping)
    df['WEEK_NUMBER'] = date.week
    df['HOUR'] = time.hour
    df['MINUTE'] = time.minute
    df = df.drop(columns=[date_col_name, time_col_name])
    return df


def main(dir_path):
    unit_summons()


if __name__ == '__main__':
    main(DIR_PATH_TOM)
