from arcgis.features import GeoAccessor
import arcpy
from arcpy.management import AddFields, CreateFeatureclass, ClearWorkspaceCache
import csv
from datetime import datetime, timezone
import numpy as np
import os
import pandas as pd
import sqlite3 as sql

def read_traffic_as_df(filepath: str) -> pd.DataFrame:
    """
    Reads the traffic file as pandas dataframe.

    :param str filepath:
    """
    traffic_df = pd.read_csv(filepath)
    traffic_df["trip_time"] = pd.to_datetime(traffic_df["trip_time"])
    return traffic_df

def read_traffic_as_sdf(filepath: str) -> GeoAccessor:
    """
    Reads the traffic file as spatially enabled dataframe.

    :param str filepath:
    """
    traffic_df = read_traffic_as_df(filepath)
    return GeoAccessor.from_xy(traffic_df, x_column="longitude", y_column="latitude")

def read_sqlite_as_df(db_filepath: str, select_statement: str, x_column: str='longitude', y_column: str='latitude') -> GeoAccessor:
    """
    Reads the data from a sqlite database into main memory using a SQL statement.
    """
    with sql.connect(db_filepath) as connection:
        return pd.read_sql_query(select_statement, connection)

def read_sqlite_as_sdf(db_filepath: str, select_statement: str, x_column: str='longitude', y_column: str='latitude') -> GeoAccessor:
    """
    Reads the data from a sqlite database into main memory using a SQL statement.
    """
    df = read_sqlite_as_df(db_filepath, select_statement, x_column, y_column)
    return GeoAccessor.from_xy(df, x_column, y_column)
        
def read_sqlite_to_featureclass(db_filepath: str, select_statement: str, x_column: str='longitude', y_column: str='latitude') -> GeoAccessor:
    """
    Reads the data from a sqlite database as an in memory feature class using a SQL statement.
    """
    filename_with_extension = os.path.basename(db_filepath)
    filename = os.path.splitext(filename_with_extension)[0]

    sdf = read_sqlite_as_sdf(db_filepath, select_statement, x_column, y_column)
    featureclass = sdf.spatial.to_featureclass("memory/" + filename)
    arcpy.management.ClearWorkspaceCache()
    return featureclass

def read_traffic_to_featureclass(filepath: str, workspace: str):
    """
    Converts the traffic data to a feature class.

    :param str filepath:    The traffic file.
    :param str workspace:   The output feature workspace.
    """
    traffic_sdf = read_traffic_as_sdf(filepath)
    return _read_traffic_to_featureclass(traffic_sdf, workspace)

def _read_traffic_to_featureclass(traffic_sdf: GeoAccessor, workspace: str):
    """
    Converts the traffic data to a feature class.

    :param str traffic_sdf: The traffic spatial dataframe.
    :param str workspace:   The output feature workspace.
    """
    featureclass = traffic_sdf.spatial.to_featureclass(f"{workspace}/traffic")
    arcpy.management.ClearWorkspaceCache()
    return featureclass

def read_traffic_as_featureclass(filepath: str, workspace: str):
    """
    Inserts the traffic data into a feature class.

    :param str filepath:    The traffic file.
    :param str workspace:   The output feature workspace. 
    """
    traffic_df = read_traffic_as_df(filepath)
    return _read_traffic_as_featureclass(traffic_df, workspace)

def read_sqlite_as_featureclass(db_filepath: str, select_statement: str):
    """
    Inserts the traffic data into an in memory feature class.

    :param str db_filepath:         The traffic sqlite file.
    :param str select_statement:    The SQL select statement.
    """
    traffic_df = read_sqlite_as_df(db_filepath, "SELECT * FROM agent_pos;")
    return _read_traffic_as_featureclass(traffic_df, "memory")

def _read_traffic_as_featureclass(traffic_df: pd.DataFrame, workspace: str):
    """
    Inserts the traffic data into a feature class.

    :param str traffic_df:  The traffic dataframe.
    :param str workspace:   The output feature workspace. 
    """
    arcpy.env.overwriteOutput = True
    feature_class_result = CreateFeatureclass(workspace, "traffic", geometry_type="POINT", spatial_reference=4326)
    feature_class = feature_class_result[0]
    
    AddFields(feature_class,
        [["id", "LONG"],
        ["trip" , "LONG"],
        ["person", "LONG"],
        ["vehicle_type", "TEXT", "vehicle_type", 256],
        ["distance_crossed", "LONG"],
        ["longitude", "DOUBLE"],
        ["latitude", "DOUBLE"],
        ["trip_time", "DATE"]])

    field_names = ["id", "trip", "person", "vehicle_type", "distance_crossed", "longitude", "latitude", "trip_time", "SHAPE@XY"]
    with arcpy.da.InsertCursor(feature_class, field_names) as insert_cursor:
        # traffic records as features

        for record in traffic_df.to_records(index=False):
            values_tuple = tuple(record)
            trip_time = record[7]
            #trip_time = datetime(year=trip_time.year, month=trip_time.month, day=trip_time.day, hour=trip_time.hour, minute=trip_time.minute, second=trip_time.second)
            # numpy.datatime64 is not valid for a feature class 
            trip_time = pd.Timestamp(trip_time)
            # concatenate tuple to 
            values_tuple = (values_tuple[0:7]) + (trip_time,) # + (values_tuple[-1],)
            # geometry (SHAPE@XY) must be a tuple
            values_tuple += ((record[5], record[6]), )
            insert_cursor.insertRow(values_tuple)
    
    # Release schema lock
    ClearWorkspaceCache()
    
    return feature_class