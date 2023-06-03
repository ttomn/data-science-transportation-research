import numpy as np
import pandas as pd
from utils import ours_read_csv

DIR_PATH_TOM = "C:\\Users\\ttomn\\OneDrive\\Desktop\\data-science-transportation-research"
DIR_PATH_MAX = "C:\\Users\\maxba\\Desktop\\Study\\Third Year\\Final Project\\data-science-transportation-research"


def sample_some_streets(dir_path: str, file_name: str, streets_amount: int):
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    df["IS_SIGNED"] = df["IS_SIGNED"].replace({'1': 1, '0': 0, 'NO': 0}).astype(np.int8)
    df.to_csv(f"{dir_path}\\final_df.csv")
    selected_values = df['ST_INDEX'].sample(n=streets_amount, random_state=42)
    filtered_df = df[df['ST_INDEX'].isin(selected_values)]
    filtered_df.to_csv(f"{dir_path}\\{streets_amount}_streets_final_df.csv")


def main(dir_path):
    sample_some_streets(dir_path,
                        "bin_removed_and_streets_data_and_speed_limits_and_humps_and_turn_traffic_calming_and_intersections_improvements_and_leading_pedestrian_and_summons_and_poi_and_collisions_and_streets.csv",
                        10000)


if __name__ == '__main__':
    main(DIR_PATH_TOM)
