import pandas as pd
from traffic.vehicle import Car



def calculate_vehicle_emissions(traffic_df: pd.DataFrame, vehicle: Car):
    """
    Calculates the vehicle emissions using a dataframe containing traffic data.

    :param DataFrame traffic_df: simulated traffic data containing agent positions
    :param Car vehicle: the vehicle being simulated
    """
    # Filter only cars
    # car_df = traffic_df["vehicle_type"] == "Car"
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

    return 42 * vehicle.carbon_equivalent
