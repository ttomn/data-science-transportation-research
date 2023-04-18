import numpy as np
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point

DIR_PATH = "C:\\Users\\ttomn\\OneDrive\\Desktop\\data-science-transportation-research"
STREET_FILE_NAME = "NYC Street Centerline (CSCL).geojson"
FILES_NAMES_TO_EXECUTE = ["Motor_Vehicle_Collisions_-_Crashes.csv",
                          "NYPD_B_Summons__Year_to_Date_.csv",
                          "NYPD_B_Summons__Historic_.csv"]
IS_GEO_FILES = False


def split_file(file_path: str, frag_amount: int):
    df = pd.read_csv(file_path)
    frag_size = df.shape[0] // frag_amount
    for i in range(frag_amount):
        frag_df = df.iloc[i * frag_size:(i + 1) * frag_size]
        frag_df.to_csv(f"{file_path[:-4]}{i}{file_path[-4:]}")


def add_columns_non_geo(streets_df, streets_buffered_df, file_name):
    df = pd.read_csv(f"{DIR_PATH}\\{file_name}")
    longitude, latitude = get_long_lat_names(df)
    df_not_na = df[(df[longitude].notna()) & (df[latitude].notna())]
    print(f"data had {df.shape[0]} rows and {df_not_na.shape[0]} have valid non-na location")

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
    df_not_na.to_csv(f"{DIR_PATH}\\with_streets_not_na_{file_name}")
    # plot_with_street_non_geo(df_not_na)


def get_long_lat_names(df):
    if "latitude" in df.columns:
        return "longitude", "latitude"
    if "Latitude" in df.columns:
        return "Longitude", "Latitude"
    if "LATITUDE" in df.columns:
        return "LONGITUDE", "LATITUDE"
    raise Exception


def add_columns_geo(streets_df, streets_buffered_df, file_name):
    pass


def plot_with_street_non_geo(df):
    longitude, latitude = get_long_lat_names(df)
    m = folium.Map(location=[40.7831, -73.9712], zoom_start=12)
    for i in range(100):
        col1 = Point(df[[longitude, latitude]].iloc[i:i + 1, ])
        folium.GeoJson(df["STREET"].iloc[i]).add_to(m)
        folium.GeoJson(col1).add_to(m)
    m.save('outcome.html')


def main():
    streets_df = gpd.read_file(f"{DIR_PATH}\\{STREET_FILE_NAME}")
    streets_df = streets_df.reset_index()
    streets_buffered_df = streets_df.buffer(0.00015)
    for file_name in FILES_NAMES_TO_EXECUTE:
        if IS_GEO_FILES:
            add_columns_geo(streets_df, streets_buffered_df, file_name)
        else:
            add_columns_non_geo(streets_df, streets_buffered_df, file_name)


if __name__ == '__main__':
    main()
