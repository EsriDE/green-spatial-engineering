import pandas as pd
import os
from arcgis.features import GeoAccessor
import arcpy

def read_traffic_as_df(filepath: str) -> pd.DataFrame:
    """
    Reads the traffic file as pandas dataframe.

    :param str filepath:
    """
    traffic_df = pd.read_csv(filepath)
    traffic_df["trip_time"] = pd.to_datetime(traffic_df["trip_time"])
    return traffic_df

def read_traffic_as_sdf(filepath: str):
    """
    Reads the traffic file as spatially enabled dataframe.

    :param str filepath:
    """
    traffic_df = read_traffic_as_df(filepath)
    return GeoAccessor.from_xy(traffic_df, x_column="longitude", y_column="latitude")

def read_traffic_to_featureclass(filepath: str):
    """
    Saves the spatially enabled dataframe as an in memory feature class.

    :param str filepath:
    """
    filename_with_extension = os.path.basename(filepath)
    filename = os.path.splitext(filename_with_extension)[0]

    traffic_sdf = read_traffic_as_sdf(filepath)
    featureclass = traffic_sdf.spatial.to_featureclass("memory/" + filename)
    arcpy.management.ClearWorkspaceCache()
    return featureclass