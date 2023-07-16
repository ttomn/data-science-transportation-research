import numpy as np
import pandas as pd
from utils import ours_read_csv

DIR_PATH_TOM = "C:\\Users\\ttomn\\OneDrive\\Desktop\\data-science-transportation-research"
DIR_PATH_MAX = "C:\\Users\\maxba\\Desktop\\Study\\Third Year\\Final Project\\data-science-transportation-research"


def sample_some_streets(dir_path: str, file_name: str, streets_amount: int):
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    selected_values = df['ST_INDEX'].sample(n=streets_amount, random_state=42)
    filtered_df = df[df['ST_INDEX'].isin(selected_values)]
    filtered_df.to_csv(f"{dir_path}\\{streets_amount}_streets_final_df.csv")


def groupby_year_street(dir_path: str, file_name: str):
    df = ours_read_csv(f"{dir_path}\\{file_name}")
    groupedby_year_street = df.groupby(['ST_INDEX', 'YEAR'])['COLLISIONS'].sum().reset_index()
    groupedby_year_street.to_csv(f"{dir_path}\\collisions_per_street_per_year.csv")


def main(dir_path):
    sample_some_streets(dir_path, "final_df.csv", 1000)


if __name__ == '__main__':
    main(DIR_PATH_TOM)
