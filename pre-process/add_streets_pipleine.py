import numpy as np
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Point


def split_file(file_path: str, frag_amount: int):
    df = pd.read_csv(file_path)
    frag_size = df.shape[0] // frag_amount
    for i in range(frag_amount):
        frag_df = df.iloc[i * frag_size:(i + 1) * frag_size]
        frag_df.to_csv(f"{file_path[:-4]}{i}{file_path[-4:]}")


def add_columns_non_geo(df, streets_df, streets_buffered_df):
    def get_closest_street(sample):
        point = Point(sample[["LONGITUDE", "LATITUDE"]])
        df_streets_filtered = streets_df[streets_buffered_df.contains(point)]
        if df_streets_filtered.shape[0] == 0:
            street_index = streets_df.distance(point).argmin()
        else:
            street_filtered_index = df_streets_filtered.distance(point).argmin()
            street_index = df_streets_filtered.iloc[street_filtered_index]["index"]
        return streets_df.iloc[street_index]["geometry"], street_index

    df[['STREET', 'ST_INDEX']] = df.apply(get_closest_street, axis=1, result_type='expand')
    return df


def plot_with_street_non_geo(df):
    m = folium.Map(location=[40.7831, -73.9712], zoom_start=12)
    for i in range(100):
        col1 = Point(df[["LONGITUDE", "LATITUDE"]].iloc[i:i + 1, ])
        folium.GeoJson(df["STREET"].iloc[i]).add_to(m)
        folium.GeoJson(col1).add_to(m)
    m.save('outcome.html')


def main():
    collisions_file_path = "C:\\Users\\ttomn\\OneDrive\\Desktop\\data-science-transportation-research" \
                           "\\Motor_Vehicle_Collisions_-_Crashes.csv"
    streets_file_path = "C:\\Users\\ttomn\\OneDrive\\Desktop\\data-science-transportation-research" \
                        "\\NYC Street Centerline (CSCL).geojson"
    collisions_df = pd.read_csv(collisions_file_path)
    streets_df = gpd.read_file(streets_file_path)
    collisions_df_not_na = collisions_df[
        (collisions_df["LONGITUDE"].notna()) & (collisions_df["LATITUDE"].notna())]
    small_collisions = collisions_df_not_na.iloc[:100]
    streets_df = streets_df.reset_index()
    streets_buffered_df = streets_df.buffer(0.00015)
    small_collisions = add_columns_non_geo(small_collisions, streets_df, streets_buffered_df)
    plot_with_street_non_geo(small_collisions)


if __name__ == '__main__':
    main()
