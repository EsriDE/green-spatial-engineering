import arcpy
from codecarbon import EmissionsTracker
from glob import glob
import logging
import os
import pandas as pd
from spatialcarbon.experiment import Experiment
from spatialcarbon.data import get_print_emissions, get_summary_emissions
from traffic.read import read_traffic_as_sdf, read_traffic_to_featureclass, read_traffic_as_featureclass



def count_persons(project_name: str, use_case: str, csv_files_pattern: str):
    """
    Determines the number of persons from the specified traffic files.

    :param str project_name: the project name e.g. "Digital Twin"
    :param str use_case: the use case e.g. "Count Travellers"
    :param str csv_files_pattern: the file pattern e.g. "data/2023-*.csv"
    """
    experiment = Experiment(project_name, use_case)
    tracker_name = experiment.create_tracker_name()
    logging.getLogger("codecarbon").info(tracker_name)
    
    # Creates a new tracker object    
    tracker = EmissionsTracker(project_name=tracker_name, output_dir="log")

    # Start tracking
    tracker.start()

    try:        
        for csv_file in glob(csv_files_pattern):
            logging.getLogger("codecarbon").info(f"Processing {csv_file} ...")
            df = pd.read_csv(csv_file)
            count_persons = df["person"].nunique()
            print(f"Es gibt insgesamt {count_persons} verschiedene Personen in der Simulation." )
    except Exception as ex:
        logging.getLogger("codecarbon").error(ex)
    finally:
        # Stop tracking
        emissions = tracker.stop()
        logging.getLogger("codecarbon").info(get_print_emissions(emissions))    

def count_persons_EsriBonn(project_name: str, use_case: str, csv_files_pattern: str):

    arcpy.env.overwriteOutput = True

    # Creates a new tracker object
    experiment = Experiment(project_name, use_case)
    tracker_name = experiment.create_tracker_name()
    logging.getLogger("codecarbon").info(tracker_name)

    tracker = EmissionsTracker(project_name=tracker_name, output_dir="log")

    # Start tracking
    tracker.start()

    try:        
        for csv_file in glob(csv_files_pattern):
            logging.getLogger("codecarbon").info(f"Processing {csv_file} ...")
            # sdf = read_traffic_as_sdf(csv_file)

            feature_class_result = read_traffic_to_featureclass(csv_file)
            # in_memory (old/ArcMap) and memory workspace

            # Esri Niederlassung Bonn
            pt = arcpy.Point(7.1156570, 50.7201054)
            pt_geometry = arcpy.PointGeometry(pt, spatial_reference=arcpy.SpatialReference(4326))

            buffer_result = arcpy.Buffer_analysis(in_features=pt_geometry, out_feature_class="memory/BufferEsriBonn", buffer_distance_or_field= "50 Meters")
            buffer = buffer_result[0]
            intersect_result = arcpy.Intersect_analysis(in_features=[feature_class_result, buffer], out_feature_class="memory/IntersectEsriBonn")
            intersect = intersect_result[0]

            values = [row[0] for row in arcpy.da.SearchCursor(intersect, "person")]
            uniqueValues = set(values)
            print(f"Es gibt insgesamt {len(uniqueValues)} verschiedene Personen, die an der Esri Niederlassung in Bonn vorbeigelaufen sind.")

            # read_traffic_as_featureclass(csv_file)
            arcpy.ClearWorkspaceCache_management()

            # clear memory workspace
            arcpy.Delete_management("memory")
    except Exception as ex:
        logging.getLogger("codecarbon").error(ex)
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
        # count_persons("DTB", "cnt P Commute Weekday", f"{traffic_dir}/commute_weekday_*.csv")

        count_persons_EsriBonn("DTB", "cnt Esri Midnight Weekday", f"{traffic_dir}/midnight_*.csv")
        # count_persons_EsriBonn("DTB", "cnt P Early Weekday", f"{traffic_dir}/early_weekday_*.csv")
        # count_persons_EsriBonn("DTB", "cnt Esri Commmute Weekday", f"{traffic_dir}/commute_weekday_*.csv")

        logging.getLogger("codecarbon").info("")
        logging.getLogger("codecarbon").info("Project summary")
        logging.getLogger("codecarbon").info("===============")
        for summary in get_summary_emissions("log/emissions.csv"):
            logging.getLogger("codecarbon").info(summary)
    except Exception as ex:
        logging.getLogger("codecarbon").error(ex)