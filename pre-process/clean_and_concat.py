import numpy as np
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point
import matplotlib.pyplot as plt
import warnings
from utils import ours_read_csv

SOURCE_FOR_COLLISIONS_TYPES_VTL = "https://ypdcrime.com/vt/vt_guide.php"
SOURCE_FOR_COLLISIONS_TYPES_NYC = "https://codelibrary.amlegal.com/codes/newyorkcity/latest/NYCrules/0-0-0" \
                                  "-63614"

warnings.filterwarnings("ignore")

DIR_PATH_TOM = "C:\\Users\\ttomn\\OneDrive\\Desktop\\data-science-transportation-research"
DIR_PATH_MAX = "C:\\Users\\maxba\\Desktop\\Study\\Third Year\\Final Project\\data-science-transportation-research"

POI_FILE = "with_streets_Points Of Interest.csv"
SUMMONS_FILE = "united_summons.csv"
CURR_SUMMONS_FILE = "with_streets_not_na_NYPD_B_Summons__Year_to_Date_.csv"
OLD_SUMMONS_FILE = "with_streets_not_na_NYPD_B_Summons__Historic_.csv"
COLLISIONS_FILE = "with_streets_not_na_Motor_Vehicle_Collisions_-_Crashes.csv"
HUMPS_FILE = "with_streets_clean_VZV_Speed Humps"
INTERSECTION_IMPROVEMENT_FILE = "with_streets_clean_VZV_Street Improvement Projects (SIPs) intersections"
LEADING_PEDESTRIAN_FILE = "with_streets_VZV_Leading Pedestrian Interval Signals.geojson"
TURN_CALMING_FILE = "with_streets_VZV_Turn Traffic Calming.geojson"

FILES_NAMES_TO_EXECUTE = [SUMMONS_FILE, OLD_SUMMONS_FILE, COLLISIONS_FILE]
COLS_TO_TAKE_FROM_SUMMONS = ["VIOLATION_DATE", "VIOLATION_TIME", "CHG_LAW_CD", "VIOLATION_CODE",
                             "VEH_CATEGORY", "STREET", "ST_INDEX"]

COLS_TO_TAKE_FROM_COLLISIONS = ['CRASH DATE', 'CRASH TIME', 'NUMBER OF PERSONS INJURED',
                                'NUMBER OF PERSONS KILLED', 'NUMBER OF PEDESTRIANS INJURED',
                                'NUMBER OF PEDESTRIANS KILLED', 'NUMBER OF CYCLIST INJURED',
                                'NUMBER OF CYCLIST KILLED', 'NUMBER OF MOTORIST INJURED',
                                'NUMBER OF MOTORIST KILLED', 'CONTRIBUTING FACTOR VEHICLE 1',
                                'CONTRIBUTING FACTOR VEHICLE 2', 'CONTRIBUTING FACTOR VEHICLE 3',
                                'CONTRIBUTING FACTOR VEHICLE 4', 'CONTRIBUTING FACTOR VEHICLE 5',
                                'VEHICLE TYPE CODE 1', 'VEHICLE TYPE CODE 2', 'VEHICLE TYPE CODE 3',
                                'VEHICLE TYPE CODE 4', 'VEHICLE TYPE CODE 5',
                                'STREET', 'ST_INDEX']

COLS_TO_TAKE_FROM_HUMPS = ("STREET", "ST_INDEX", "end_date", "humps_amount")

COLS_TO_TAKE_FROM_INTERSECTION_IMPROVEMENT = ("STREET", "ST_INDEX", "end_date")

COLS_TO_TAKE_FROM_LEADING_PEDESTRIAN = ("STREET", "ST_INDEX", "install_da")

COLS_TO_TAKE_FROM_TURN_CALMING = ("STREET", "ST_INDEX", "completion")

COLS_TO_TAKE_FROM_POI = ["created", "facility_t", 'STREET', 'ST_INDEX']

PARAMS_FOR_PROCESS = {
    COLLISIONS_FILE: [COLS_TO_TAKE_FROM_COLLISIONS, 'CRASH DATE', 'CRASH TIME'],
    SUMMONS_FILE: [COLS_TO_TAKE_FROM_SUMMONS, "VIOLATION_DATE", "VIOLATION_TIME"],
    POI_FILE: [COLS_TO_TAKE_FROM_POI, "created", None],
    HUMPS_FILE: [COLS_TO_TAKE_FROM_HUMPS, 'end_date'],
    INTERSECTION_IMPROVEMENT_FILE: [COLS_TO_TAKE_FROM_INTERSECTION_IMPROVEMENT, "end_date"],
    LEADING_PEDESTRIAN_FILE: [COLS_TO_TAKE_FROM_LEADING_PEDESTRIAN, "install_da"],
    TURN_CALMING_FILE: [COLS_TO_TAKE_FROM_TURN_CALMING, "completion"]
}
POI_MAPPING = {
    1: "Residential",
    2: "Education",
    3: "Cultural",
    4: "Recreational",
    5: "Social Services",
    6: "Transportation",
    7: "Commercial",
    8: "Government",
    9: "Religious Institution",
    10: "Health Services",
    11: "Public Safety",
    12: "Water",
    13: "Miscellaneous"
}

weekday_mapping = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
}


def split_file(file_path: str, frag_amount: int):
    df = ours_read_csv(file_path)
    frag_size = df.shape[0] // frag_amount
    for i in range(frag_amount):
        frag_df = df.iloc[i * frag_size:(i + 1) * frag_size]
        frag_df.to_csv(f"{file_path[:-4]}{i}{file_path[-4:]}")


def unite_file(file_path: str, frag_amount: int):
    dfs = []
    for i in range(frag_amount):
        dfs.append(ours_read_csv(f"{file_path[:-4]}{i}{file_path[-4:]}"))
    df = pd.concat(dfs)
    df.to_csv(file_path)


def unit_summons(dir_path):
    summons_df = ours_read_csv(f"{dir_path}\\{CURR_SUMMONS_FILE}")
    old_summons_df = ours_read_csv(f"{DIR_PATH_TOM}\\{OLD_SUMMONS_FILE}")
    summons_df = create_summons_cols(summons_df)
    old_summons_df = create_summons_cols(old_summons_df)
    all_summons = pd.concat([summons_df, old_summons_df], axis=0)
    all_summons.to_csv(f"{dir_path}\\{SUMMONS_FILE}")


def create_summons_cols(df):
    df = df[COLS_TO_TAKE_FROM_SUMMONS]
    df = get_timing_cols(df, date_col_name="VIOLATION_DATE", time_col_name="VIOLATION_TIME")
    return df


def aggregate_dfs(dir_path, files_names, cols_to_aggregate):
    for file_name in files_names:
        print(f"Start execute file {file_name}:")
        df = ours_read_csv(f"{dir_path}\\{file_name}")
        df_params = PARAMS_FOR_PROCESS[file_name]
        df = df[df_params[0]]
        df = get_timing_cols(df, df_params[1], df_params[2])
        df.to_csv(f"{dir_path}\\timed_{file_name}")
        df = agg_by_time_and_loc(df, cols_to_aggregate)
        df.to_csv(f"{dir_path}\\agg_{file_name}")
        print(f"\n\n\n############################################")
        print(f"Finished execute file {file_name}")
        print(f"############################################\n\n\n")


def get_timing_cols(df, date_col_name, time_col_name=None):
    date = pd.DatetimeIndex(df[date_col_name])
    df['MONTH'] = date.month
    df['YEAR'] = date.year
    df['DAY'] = date.day
    df['DAY_OF_WEEK'] = date.day_name().map(weekday_mapping)
    df['WEEK_NUMBER'] = date.week
    if time_col_name is not None:
        time = pd.DatetimeIndex(df[time_col_name])
        df['HOUR'] = time.hour
        df['MINUTE'] = time.minute
        df = df.drop(columns=[date_col_name, time_col_name])
    else:
        df = df.drop(columns=[date_col_name])
    return df


def get_timing_cols_geo(df, date_col_name):
    date = pd.DatetimeIndex(df[date_col_name])
    df['MONTH'] = date.month
    df['YEAR'] = date.year
    df['DAY'] = date.day
    df['DAY_OF_WEEK'] = date.day_name().map(weekday_mapping)
    df['WEEK_NUMBER'] = date.week
    df = df.drop(columns=[date_col_name])
    return df


def get_date_cols_geo_files(dir_path, files_names, cols_to_aggregate):
    for file_name in files_names:
        print(f"Start execute file {file_name}:")
        df = ours_read_csv(f"{dir_path}\\{file_name}")
        # df_params = PARAMS_FOR_PROCESS[file_name]
        # df = df[list(df_params[0])]
        # df = get_timing_cols_geo(df, df_params[1])
        # df.to_csv(f"{dir_path}\\timed_{file_name}.csv")
        df = agg_by_time_and_loc(df, cols_to_aggregate)
        df.to_csv(f"{dir_path}\\agg_{file_name}")
        print(f"\n\n\n############################################")
        print(f"Finished execute file {file_name}")
        print(f"############################################\n\n\n")


def agg_by_time_and_loc(df, cols_to_aggregate):
    new_col_name = "AMOUNT"
    for col in cols_to_aggregate:
        new_col_name += ("_" + col)
    agg_df = df.groupby(cols_to_aggregate).size().reset_index()
    agg_df = agg_df.rename(columns={0: new_col_name})
    return agg_df


def remove_zero_lat_long_from_colli(dir_path, file_name):
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    filtered_df = df[
        (df["LATITUDE"] > 40) & (df["LATITUDE"] < 42) & (df["LONGITUDE"] > -75) & (df["LONGITUDE"] < -73)]
    df_params = PARAMS_FOR_PROCESS[file_name]
    filtered_df = filtered_df[df_params[0]]
    filtered_df = get_timing_cols(filtered_df, df_params[1], df_params[2])
    filtered_df.to_csv(f"{dir_path}\\timed_with_streets_not_na_Motor_Vehicle_Collisions_-_Crashes.csv")


def bin_summons(dir_path, file_name):
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    vtl_filter = df["CHG_LAW_CD"] == "VTL"
    df["VTL_NUMBERS"] = 0
    vtl_numbers = df.loc[vtl_filter, "VIOLATION_CODE"].str.extract(r'^(\d+)', expand=False)
    three_digits_filter = (~ vtl_numbers.str.startswith('1')) & (~ vtl_numbers.str.startswith('2'))
    vtl_numbers[three_digits_filter] = vtl_numbers[three_digits_filter].astype(str).str.slice(stop=3)
    df.loc[vtl_filter, "VTL_NUMBERS"] = vtl_numbers
    return df


def ohe_poi(dir_path, file_name):
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    one_hot_df = pd.get_dummies(df["facility_t"])
    one_hot_df.columns = POI_MAPPING.values()
    df = pd.concat([df, one_hot_df], axis=1)
    df = df.drop(columns="facility_t")
    df.to_csv(f"{dir_path}\\ohe_{file_name}")
    return df


def sum_poi_in_same_street(dir_path, file_name):
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    df = df.drop(columns=["STREET", "MONTH", "YEAR", "DAY", "DAY_OF_WEEK", "WEEK_NUMBER"])
    df = df.groupby("ST_INDEX").sum().reset_index(names="ST_INDEX")
    df.to_csv(f"{dir_path}\\sumed_{file_name}")


def create_main_df(dir_path, main_file):
    main_df = ours_read_csv(f"{dir_path}\\{main_file}")
    main_df = main_df.reset_index(names="ST_INDEX")
    main_df = main_df[["ST_INDEX", "the_geom"]]
    month_df = pd.DataFrame({"MONTH": np.arange(1, 13)})
    year_df = pd.DataFrame({"YEAR": np.arange(2012, 2024)})
    main_df = main_df.merge(month_df, how="cross").merge(year_df, how="cross")
    main_df.to_csv(f"{dir_path}\\timed_{main_file}")


def concat_colli_df(dir_path, main_file, file_name):
    main_df = ours_read_csv(f"{dir_path}\\{main_file}")
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    df_merged = pd.merge(main_df, df, on=['ST_INDEX', "YEAR", "MONTH"], how='left')
    # df_merged = df_merged.drop(columns="STREET")
    df_merged["AMOUNT_ST_INDEX_YEAR_MONTH"] = df_merged["AMOUNT_ST_INDEX_YEAR_MONTH"].fillna(0)
    df_merged = df_merged.rename(columns={"AMOUNT_ST_INDEX_YEAR_MONTH": "collisions"})
    df_merged = df_merged.rename(columns={"collisions": "COLLISIONS"})
    df_merged.to_csv(f"{dir_path}\\collisions_and_streets.csv")


def concat_poi_df(dir_path, main_file, file_name):
    main_df = ours_read_csv(f"{dir_path}\\{main_file}")
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    df_merged = pd.merge(main_df, df, on=['ST_INDEX'], how='left')
    df_merged.iloc[:, -13:] = df_merged.iloc[:, -13:].fillna(0)
    df_merged.to_csv(f"{dir_path}\\poi_and_{main_file}")


def concat_summons_df(dir_path, main_file, file_name):
    main_df = ours_read_csv(f"{dir_path}\\{main_file}")
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    df = df.rename(columns={"AMOUNT_ST_INDEX_YEAR_MONTH": "SUMMONS"})
    df_merged = pd.merge(main_df, df, on=['ST_INDEX', "YEAR", "MONTH"], how='left')
    # df_merged = df_merged.drop(columns="STREET")
    df_merged["SUMMONS"] = df_merged["SUMMONS"].fillna(0)
    df_merged.to_csv(f"{dir_path}\\summons_and_{main_file}")


def concat_binary_column_df(dir_path, main_file, file_name, new_binary_column, new_file_name):
    main_df = ours_read_csv(f"{dir_path}\\{main_file}")
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    df = df.drop(columns=["DAY", "DAY_OF_WEEK", "WEEK_NUMBER"])
    df = df[df['YEAR'] >= 2012]
    df = df.drop_duplicates(subset=['ST_INDEX', 'MONTH', 'YEAR'])
    df_merged = pd.merge(main_df, df, on=['ST_INDEX', "YEAR", "MONTH"], how='left')
    df_merged[new_binary_column] = 0
    df_merged.loc[df_merged['STREET'].notna(), new_binary_column] = 1
    df_merged = df_merged.drop(columns=["STREET"])
    df_merged = df_merged.sort_values(['ST_INDEX', 'YEAR', 'MONTH'])
    groups = df_merged.groupby('ST_INDEX')
    df_merged[new_binary_column] = groups[new_binary_column].cummax()
    df_merged.to_csv(f"{dir_path}\\{new_file_name}{main_file}")


def concat_speed_humps_df(dir_path, main_file, file_name):
    main_df = ours_read_csv(f"{dir_path}\\{main_file}")
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    df_speed_humps_no_dup = clean_speed_humps(df)
    df_merged = pd.merge(main_df, df_speed_humps_no_dup, on=['ST_INDEX', "YEAR", "MONTH"], how='left')
    df_merged["HUMPS"] = df_merged["HUMPS"].fillna(0)
    df_merged.sort_values(['ST_INDEX', 'YEAR', 'MONTH'], inplace=True)
    groups = df_merged.groupby('ST_INDEX')
    df_merged['HUMPS'] = groups['HUMPS'].cummax()
    df_merged = df_merged.drop(columns=["STREET"])
    df_merged.to_csv(f"{dir_path}\\humps_and_{main_file}")


def clean_speed_humps(df):
    df = df.drop(columns=["DAY", "DAY_OF_WEEK", "WEEK_NUMBER"])
    mask = df['YEAR'] < 2012
    df.loc[mask, 'YEAR'] = 2012
    df.loc[mask, 'MONTH'] = 1
    max_humps = df.groupby(['ST_INDEX', 'YEAR', 'MONTH'])['humps_amount'].max().reset_index()
    # merge the max_humps DataFrame back into the original DataFrame
    df_no_dup = pd.merge(df, max_humps, on=['ST_INDEX', 'YEAR', 'MONTH'], how='left')
    df_no_dup.drop(columns="humps_amount_x", inplace=True)
    df_no_dup.rename(columns={'humps_amount_y': 'HUMPS'}, inplace=True)
    df_speed_humps_no_dup = df_no_dup.drop_duplicates(subset=['ST_INDEX', 'MONTH', 'YEAR'])
    return df_speed_humps_no_dup


def remove_future_data(dir_path, file_name):
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    df = df[(df['MONTH'] < 3) | (df['YEAR'] < 2023)]
    df.to_csv(f"{dir_path}\\{file_name}")


def concat_speed_limits(dir_path, main_file, file_name):
    main_df = ours_read_csv(f"{dir_path}\\{main_file}")
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    df_clean_speed_limits = df.drop(columns=['shape_leng', 'street', 'geometry'])
    df_clean_speed_limits = df_clean_speed_limits.rename(
        columns={'postvz_sg': 'IS_SIGNED', 'postvz_sl': 'SPEED_LIMIT'})
    df_clean_speed_limits = df_clean_speed_limits.groupby('ST_INDEX').last().reset_index()
    df_merged = pd.merge(main_df, df_clean_speed_limits, on=['ST_INDEX'], how='left')
    df_merged['SPEED_LIMIT'] = df_merged['SPEED_LIMIT'].fillna(25)
    df_merged.loc[df_merged['IS_SIGNED'] == 'YES', 'IS_SIGNED'] = 1
    df_merged['IS_SIGNED'] = df_merged['IS_SIGNED'].fillna(0)
    if "STREET" in df_merged.columns:
        df_merged = df_merged.drop(columns=["STREET"])
    df_merged.to_csv(f"{dir_path}\\speed_limits_and_{main_file}")


def concat_streets_data(dir_path, main_file, file_name):
    # main_df = ours_read_csv(f"{dir_path}\\{main_file}")
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    print("hi")


def main(dir_path):
    # get_date_cols_geo_files(dir_path=dir_path,
    #                         files_names=["timed_with_streets_not_na_Motor_Vehicle_Collisions_-_Crashes.csv",
    #                             "united_summons.csv"],
    #                         cols_to_aggregate=['ST_INDEX', 'YEAR', 'MONTH'])
    # concat_summons_df(dir_path, main_file="poi_and_collisions_and_streets.csv",
    #                   file_name="agg_united_summons.csv")
    # split_file(file_path=f"{dir_path}\\summons_and_poi_and_collisions_and_streets.csv", frag_amount=5)
    # create_main_df(dir_path, "Centerline.csv")
    # concat_summons_df(dir_path, "poi_and_collisions_and_streets.csv",
    #                   "agg_united_summons.csv")
    # df_streets = ours_read_csv(f"{dir_path}\\Centerline.csv")
    # df = ours_read_csv(f"{dir_path}\\agg_timed_with_streets_not_na_Motor_Vehicle_Collisions_-_Crashes.csv")
    # ohe_poi(dir_path, "timed_with_streets_Points Of Interest.csv")
    # aggregate_dfs(dir_path, files_names=[POI_FILE],
    #               cols_to_aggregate=["YEAR", "MONTH", "ST_INDEX"])
    # bin_summons(dir_path, SUMMONS_FILE)

    # unit_summons(dir_path)
    # aggregate_dfs(dir_path, files_names=["with_streets_not_na_Motor_Vehicle_Collisions_-_Crashes.csv"],
    #             cols_to_aggregate=["YEAR", "MONTH"])
    # concat_binary_column_df(dir_path,
    #                         "summons_and_poi_and_collisions_and_streets.csv",
    #                         "timed_with_streets_VZV_Leading Pedestrian Interval Signals.geojson.csv",
    #                         "PEDESTRIAN_BINARY",
    #                         "leading_pedestrian_and_")

    # concat_binary_column_df(dir_path,
    #                         "leading_pedestrian_and_summons_and_poi_and_collisions_and_streets.csv",
    #                         "timed_with_streets_clean_VZV_Street Improvement Projects (SIPs) intersections.csv",
    #                         "INTERSECTIONS_BINARY",
    #                         "intersections_improvements_and_")
    #
    # concat_binary_column_df(dir_path,
    #                         "intersections_improvements_and_leading_pedestrian_and_summons_and_poi_and_collisions_and_streets.csv",
    #                         "timed_with_streets_VZV_Turn Traffic Calming.geojson.csv",
    #                         "TURN_TRAFFIC_BINARY",
    #                         "turn_traffic_calming_and_")
    #
    # concat_speed_humps_df(dir_path,
    #                       "turn_traffic_calming_and_intersections_improvements_and_leading_pedestrian_and_summons_and_poi_and_collisions_and_streets.csv",
    #                       "timed_with_streets_clean_VZV_Speed Humps.csv")
    # concat_speed_limits(dir_path, main_file="humps_and_turn_traffic_calming_and_intersections_improvements_and_leading_pedestrian_and_summons_and_poi_and_collisions_and_streets.csv", file_name="with_streets_clean_VZV_Speed Limits.geojson")
    concat_streets_data(dir_path,
              main_file="speed_limits_and_humps_and_turn_traffic_calming_and_intersections_improvements_and_leading_pedestrian_and_summons_and_poi_and_collisions_and_streets.csv", file_name="Centerline.csv")


if __name__ == '__main__':
    main(DIR_PATH_TOM)
