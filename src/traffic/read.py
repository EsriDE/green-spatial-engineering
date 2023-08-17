from arcgis.features import GeoAccessor
import arcpy
from arcpy.management import AddFields, CreateFeatureclass, ClearWorkspaceCache
import csv
from datetime import datetime, timezone
import numpy as np
import os
import pandas as pd

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

def read_traffic_as_featureclass(workspace: str, filepath: str):
    """
    Saves the traffic data as an in memory feature class.

    :param str filepath:
    """
    arcpy.env.overwriteOutput = True
    
    filename_with_extension = os.path.basename(filepath)
    filename = os.path.splitext(filename_with_extension)[0]

    # Siehe hier: https://github.com/esride-jts/geoint-toolbox/blob/master/src/geoint/gdelt_workspace.py

    # featureclass = arcpy.management.CreateFeatureclass("C:/src/", filename)
    # fields = arcpy.ListFields(filepath)
    # for field in fields:
    #     # arcpy.management.AddField("C:/src/" + filename + ".shp", field.baseName, field.type)
    #     print(field.baseName, field.type)
    # featureclass = arcpy.management.AddFields("C:/src/" + filename + ".shp", 
    #                            [["id", "LONG"],
    #                             ["trip" , "LONG"],
    #                             ["person", "LONG"],
    #                             ["vehic_type", "TEXT", "vehicle_type"],
    #                             ["dist_crd", "LONG", "distance_crossed"],
    #                             ["longitude", "DOUBLE"],
    #                             ["latitude", "DOUBLE"],
    #                             ["trip_time", "DATE"]])
    # print(fields)
    # featureclass.to_featurelayer(title='Carbon Emissions', folder='Stadt Bonn', tags=['Open Data', 'Carbon', 'Digital Twin'])

    # output = "in_memory/traffic_featureclass"
    # output = "C:/src/Data.gdb/" + filename

    # crs = arcpy.SpatialReference(4326)
    # arcpy.management.XYTableToPoint(in_table=filepath, out_feature_class = output + filename, x_field="longitude", y_field="latitude", coordinate_system=crs)
    # arcpy.management.CalculateField(in_table=output, field="trip_time1", expression="!trip_time!", expression_type="PYTHON3", field_type="DATE")
    # arcpy.management.DeleteField(in_table=output, drop_field="trip_time", method="DELETE_FIELDS")

    # arcpy.management.AlterField("C:/src/" + filename + ".shp", "trip_time", "trip_time1")

    # trip time as DATE as so on
    # field_names = [field.name for field in arcpy.ListFields(featureclass)]

    traffic_df = read_traffic_as_df(filepath)    
    #traffic_df["trip_time"] = traffic_df["trip_time"].apply(lambda trip_time: datetime(trip_time.year, trip_time.month, trip_time.day)) #traffic_df["trip_time"].apply(lambda datetime: datetime.isoformat())
    #traffic_df["XY"] = list(zip(traffic_df["longitude"], traffic_df["latitude"]))
    #traffic_np = traffic_df.to_records(index=False)
    
    feature_class_result = CreateFeatureclass(workspace, filename, geometry_type="POINT", spatial_reference=4326)
    feature_class = feature_class_result[0]

    for column in traffic_df.columns:
        pass
    
    AddFields(feature_class,
        [["id", "LONG"],
        ["trip" , "LONG"],
        ["person", "LONG"],
        ["vehicle_type", "TEXT", "vehicle_type", 256],
        ["distance_crossed", "LONG"],
        ["longitude", "DOUBLE"],
        ["latitude", "DOUBLE"],
        ["trip_time", "DATE"]])
    
    """
    #outFC = "C:/src/Data.gdb/" + filename

    # Create a numpy array with an id field, and a field with a tuple
    #  of x,y coordinates
    # array = numpy.array(
    #     [
    #         (1, (7.1156570, 50.7201054)),
    #         (2, (7.8156570, 50.0201054)),
    #     ],
    #     numpy.dtype([("idfield", numpy.int32), ("XY", "<f8", 2)]),
    # )

    # Define a spatial reference for the output feature class
    spatial_ref = arcpy.SpatialReference(4326)

    # Export the numpy array to a feature class using the XY field to
    # represent the output point feature
    #arcpy.da.NumPyArrayToFeatureClass(my_data, outFC, ["longitude", "latitude"], spatial_ref)

    return
    # print(field_names)
    # arcpy.management.AddFields()



    # print(csv_rows)
    # print(pd.DataFrame(csv_rows))
    """

    field_names = ["id", "trip", "person", "vehicle_type", "distance_crossed", "longitude", "latitude", "trip_time", "SHAPE@XY"]
    with arcpy.da.InsertCursor(feature_class, field_names) as insert_cursor:
        # traffic records as features

        # for i in csv_rows:
        #     insert_cursor.inserRow([])
        # for i in range(0,25):
        #     insert_cursor.insertRow([i, "Polygon", 3 , 100, 10, "15", 5, 7, 52, "16.08.2023"])
        for record in traffic_df.to_records(index=False):
            values_tuple = tuple(record)
            trip_time = record[7]
            #trip_time = datetime(year=trip_time.year, month=trip_time.month, day=trip_time.day, hour=trip_time.hour, minute=trip_time.minute, second=trip_time.second)
            trip_time = pd.Timestamp(trip_time)
            values_tuple = (values_tuple[0:7]) + (trip_time,)# + (values_tuple[-1],)
            values_tuple += ((record[5], record[6]), )
            insert_cursor.insertRow(values_tuple)
    
    # Release schema lock
    ClearWorkspaceCache()
    
    return feature_class