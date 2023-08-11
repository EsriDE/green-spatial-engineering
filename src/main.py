from arcgis.geometry import Point
from codecarbon import EmissionsTracker
from glob import glob
import logging
import os
import pandas as pd
from spatialcarbon.experiment import Experiment
from spatialcarbon.data import get_print_emissions, get_summary_emissions
from traffic.read import read_traffic_as_sdf



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
        logging.getLogger("codecarbon").info(get_print_emissions(emissions))    

def count_persons_EsriBonn(project_name: str, use_case: str, csv_files_pattern: str):

    pt = Point({"x" : -118.15, "y" : 33.80, 
            "spatialReference" : {"wkid" : 4326}})
    # type(pt)

    # Read as spatial enabled dataframe

    # Creates a new tracker object
    experiment = Experiment(project_name, use_case)
    tracker_name = experiment.create_tracker_name()
    tracker = EmissionsTracker(project_name=tracker_name, output_dir="log")

    # Start tracking
    tracker.start()

    try:        
        for csv_file in glob(csv_files_pattern):
            sdf = read_traffic_as_sdf(csv_file)
            count_persons = sdf["person"].nunique()
    except Exception as ex:
        logging.error(ex)
    finally:
        # Stop tracking
        emissions = tracker.stop()
        logging.getLogger("codecarbon").info(get_print_emissions(emissions))



if __name__=="__main__":

    logging.basicConfig()
    logger = logging.getLogger("codecarbon")
    
    traffic_dir = os.getenv("TRAFFIC_DIR")
    
    try:
        if None is traffic_dir:
            raise ValueError("Traffic directory not specified!")

        count_persons("DTB", "cnt P Midnight", f"{traffic_dir}/midnight_*.csv")
        count_persons("DTB", "cnt P Early Weekday", f"{traffic_dir}/early_weekday_*.csv")
        count_persons("DTB", "cnt P Commute Weekday", f"{traffic_dir}/commute_weekday_*.csv")
        count_persons_EsriBonn("DTB", "cnt Esri Commmute Weekday", f"{traffic_dir}/commute_weekday_*.csv")

        logging.getLogger("codecarbon").info("")
        logging.getLogger("codecarbon").info("Project summary")
        logging.getLogger("codecarbon").info("===============")
        for summary in get_summary_emissions("log/emissions.csv"):
            logging.getLogger("codecarbon").info(summary)
    except Exception as ex:
        logger.error(ex)