import arcpy
import pandas as pd
from traffic.vehicle import Car



def calculate_vehicle_emissions(traffic_df: pd.DataFrame, vehicle: Car):
    """
    Calculates the vehicle emissions using a dataframe containing traffic data.

    :param DataFrame traffic_df: simulated traffic data containing agent positions
    :param Car vehicle: the vehicle being simulated
    """
    # Filter only cars
    car_df = traffic_df.loc[traffic_df["vehicle_type"] == "Car"]
    # print(car_df)

    # car_df_4384 = car_df.loc[car_df["trip"] == 4384] # 31.118.831 # 3,5108544549638765
    # print(car_df_1537)

    coordinates = car_df[["longitude", "latitude"]].values.tolist()
    
    coordinates_array = arcpy.Array([arcpy.Point(coord[0], coord[1]) for coord in coordinates])

    tripline = arcpy.Polyline(coordinates_array, spatial_reference=arcpy.SpatialReference(4326))
    total_distance = tripline.getLength(method="GEODESIC", units="Kilometers")
    
    # car_df_1537 = car_df_1537.loc[car_df_1537["distance_crossed"].idxmax()]
    # print(car_df_4384)



    # 
    # Query the max distance_crossed for every trip
    # Group by trip => max distance crossed
    # distance_crossed could be meters or unknown map units?
    # distances[trip] = max(traffic_df["distance_crossed"])
    #
    # or if distance_crossed is unknown map unit
    # construct tracks as Polyline (https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/polyline.htm)
    # distances[trip] = calculate Polyline.getLength("GEODESIC", "Kilometers")
    #
    # total_distance = sum(distances)
    # return carbon_equivalent * total_distance

    return total_distance * vehicle.carbon_equivalent
