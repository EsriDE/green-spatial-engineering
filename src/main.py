from arcgis.geometry import Point
from codecarbon import EmissionsTracker
from glob import glob
import logging
import os
import pandas as pd
from spatialcarbon.experiment import Experiment



def count_persons(project_name: str, use_case: str, csv_files_pattern: str):
    """
    Determines the number of persons from the specified traffic files.

    :param str project_name: the project name e.g. "Digital Twin"
    :param str use_case: the use case e.g. "Count Travellers"
    :param str csv_files_pattern: the file pattern e.g. "data/2023-*.csv"
    """
    experiment = Experiment(project_name, use_case)
    tracker_name = experiment.create_tracker_name()
    
    # Creates a new tracker object    
    tracker = EmissionsTracker(project_name=tracker_name, output_dir="log")

    # Start tracking
    tracker.start()

    try:        
        for csv_file in glob(csv_files_pattern):
            df = pd.read_csv(csv_file)
            count_persons = df["person"].nunique()
    except Exception as ex:
        logging.error(ex)
    finally:
        # Stop tracking
        emissions = tracker.stop()
        print(emissions)
    

def count_persons_EsriBonn():

    pt = Point({"x" : -118.15, "y" : 33.80, 
            "spatialReference" : {"wkid" : 4326}})
    return type(pt)

if __name__=="__main__":

    traffic_dir = os.getenv("TRAFFIC_DIR")

    try:
        count_persons("DTB", "cnt P Midnight", f"{traffic_dir}/midnight_*.csv")
        count_persons("DTB", "cnt P Early Weekday", f"{traffic_dir}/early_weekday_*.csv")
        count_persons_EsriBonn()
    except Exception as ex:
        logging.error(ex)