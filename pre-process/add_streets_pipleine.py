import numpy as np
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point
import warnings

warnings.filterwarnings("ignore")

DIR_PATH_TOM = "C:\\Users\\ttomn\\OneDrive\\Desktop\\data-science-transportation-research"
DIR_PATH_MAX = "C:\\Users\\maxba\\Desktop\\Study\\Third Year\\Final Project\\data-science-transportation-research"
STREET_FILE_NAME = "NYC Street Centerline (CSCL).geojson"

# FILES_NAMES_TO_EXECUTE = ["Motor_Vehicle_Collisions_-_Crashes.csv",
#                          "NYPD_B_Summons__Year_to_Date_.csv",
#                          "NYPD_B_Summons__Historic_.csv"]

GEO_FILES_NAMES_TO_EXECUTE = ["VZV_Speed Humps.geojson",
                              "VZV_Speed Limits.geojson",
                              "VZV_Leading Pedestrian Interval Signals.geojson",
                              "VZV_Street Improvement Projects (SIPs) intersections.geojson",
                              "VZV_Turn Traffic Calming.geojson",
                              "Points Of Interest.geojson"]

IS_GEO_FILES = True
IS_NON_GEO_FILES = False


def split_file(file_path: str, frag_amount: int):
    df = pd.read_csv(file_path)
    frag_size = df.shape[0] // frag_amount
    for i in range(frag_amount):
        frag_df = df.iloc[i * frag_size:(i + 1) * frag_size]
        frag_df.to_csv(f"{file_path[:-4]}{i}{file_path[-4:]}")


def add_columns_non_geo(streets_df, streets_buffered_df, dir_path, file_name):
    df = pd.read_csv(f"{dir_path}\\{file_name}")
    longitude, latitude = get_long_lat_names(df)
    df_not_na = df[(df[longitude].notna()) & (df[latitude].notna())]
    print(f"data had {df.shape[0]}"
          f"rows and {df_not_na.shape[0]} have valid non-n"
          f"location")

    def get_closest_street(sample):
        point = Point(sample[[longitude, latitude]])
        df_streets_filtered = streets_df[streets_buffered_df.contains(point)]
        if df_streets_filtered.shape[0] == 0:
            street_index = streets_df.distance(point).argmin()
        else:
            street_filtered_index = df_streets_filtered.distance(point).argmin()
            street_index = df_streets_filtered.iloc[street_filtered_index]["index"]
        return streets_df.iloc[street_index]["geometry"], street_index

    df_not_na[['STREET', 'ST_INDEX']] = df_not_na.apply(get_closest_street, axis=1, result_type='expand')
    df_not_na.to_csv(f"{dir_path}\\with_streets_not_na_{file_name}")
    # plot_with_street_non_geo(df_not_na)


def get_long_lat_names(df):
    if "latitude" in df.columns:
        return "longitude", "latitude"
    if "Latitude" in df.columns:
        return "Longitude", "Latitude"
    if "LATITUDE" in df.columns:
        return "LONGITUDE", "LATITUDE"
    raise Exception


non_intersect_counter = 0


def add_columns_geo(streets_df, streets_buffered_df, dir_path, file_name):
    print(f"Starting to proccess {file_name}")
    df = gpd.read_file(f"{dir_path}\\{file_name}")
    global non_intersect_counter
    non_intersect_counter = 0

    def get_closest_street(sample):
        sample_location = sample["geometry"]
        df_streets_filtered = streets_df[streets_buffered_df.intersects(sample_location)]
        if df_streets_filtered.shape[0] == 0:
            street_index = streets_df.distance(sample["geometry"]).argmin()
            global non_intersect_counter
            non_intersect_counter += 1
        else:
            inter = df_streets_filtered.intersection(sample_location)
            uni = df_streets_filtered.union(sample_location)
            street_filtered_index = (inter.area / uni.area).argmax()
            street_index = df_streets_filtered.iloc[street_filtered_index]["index"]
        return streets_df.iloc[street_index]["geometry"], street_index

    df[['STREET', 'ST_INDEX']] = df.apply(get_closest_street, axis=1, result_type='expand')
    print(f"data: {file_name} had {non_intersect_counter}"
          f" number of items with no intersection with a street.")
    print(f"data have {df.shape[0]}"
          f" rows and {df['ST_INDEX'].isna().sum()} st_index null values and "
          f"{df['STREET'].isna().sum()} street null values")
    df.to_csv(f"{dir_path}\\with_streets_{file_name}")
    # plot_with_street_geo_data(df)


def plot_with_street_non_geo(df):
    longitude, latitude = get_long_lat_names(df)
    m = folium.Map(location=[40.7831, -73.9712], zoom_start=12)
    for i in range(100):
        col1 = Point(df[[longitude, latitude]].iloc[i:i + 1, ])
        folium.GeoJson(df["STREET"].iloc[i]).add_to(m)
        folium.GeoJson(col1).add_to(m)
    m.save('outcome.html')


def plot_with_street_geo_data(df):
    m = folium.Map(location=[40.7831, -73.9712], zoom_start=12)
    for i in range(100):
        col1 = df["geometry"].iloc[i:i + 1, ]
        folium.GeoJson(df["STREET"].iloc[i]).add_to(m)
        folium.GeoJson(col1).add_to(m)
    m.save('outcome.html')


def main(dir_path):
    streets_df = gpd.read_file(f"{dir_path}\\{STREET_FILE_NAME}")
    streets_df = streets_df.reset_index()
    streets_buffered_df = streets_df.buffer(0.00015)
    for file_name in GEO_FILES_NAMES_TO_EXECUTE:
        if IS_GEO_FILES:
            add_columns_geo(streets_df, streets_buffered_df, dir_path, file_name)
        if IS_NON_GEO_FILES:
            add_columns_non_geo(streets_df, streets_buffered_df, dir_path, file_name)


if __name__ == '__main__':
    main(DIR_PATH_TOM)
