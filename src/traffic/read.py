import pandas as pd
from arcgis.features import GeoAccessor

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