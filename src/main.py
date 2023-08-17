from arcgis.geometry import Point, buffer
from arcgis.gis import GIS
from getpass import getpass
import arcgis
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
    except Exception as ex:
        logging.getLogger("codecarbon").error(ex)
    finally:
        # Stop tracking
        emissions = tracker.stop()
        logging.getLogger("codecarbon").info(get_print_emissions(emissions))    

def count_persons_EsriBonn(project_name: str, use_case: str, csv_files_pattern: str):

    arcpy.env.overwriteOutput = True

    # gis = GIS("pro")

    # pt = Point({"x" : 7.1156570, "y" : 50.7201054, "spatialReference" : {"wkid" : 4326}})
    pt = arcpy.Point(7.1156570, 50.7201054)
    pt_geometry = arcpy.PointGeometry(pt, spatial_reference=arcpy.SpatialReference(4326))
    # type(pt)
    # input_layer = "https://services3.arcgis.com/GVgbJbqm8hXASVYi/arcgis/rest/services/Portland%20Bike%20Routes/FeatureServer/0"
    # arcgis.features.analysis.create_buffers(input_layer=pt, distances=[50], units="Meters", output_name="create_buffers")

    # buff = buffer(geometries=pt, in_sr=4326, distances=[50], unit="Meters")
    # print(buff)
    # Read as spatial enabled dataframe

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

            # rename variable (file)
            file = read_traffic_to_featureclass(csv_file)
            # count_persons = sdf["person"].nunique()
            # count_persons = arcpy.management.GetCount(file)
            # in_memory (old/ArcMap) und memory workspace 

            # result objekt geben lassen
            arcpy.Buffer_analysis(in_features=pt_geometry, out_feature_class="in_memory/BufferEsriBonn", buffer_distance_or_field= "50 Meters")
            arcpy.Intersect_analysis(in_features=[file, "in_memory/BufferEsriBonn"], out_feature_class="in_memory/IntersectEsriBonn")

            values = [row[0] for row in arcpy.da.SearchCursor("in_memory/IntersectEsriBonn", "person")]
            uniqueValues = set(values)
            print("Es gibt insgesamt " + str(len(uniqueValues)) + " verschiedene Personen, die an der Esri Niederlassung in Bonn vorbeigelaufen sind.")

            read_traffic_as_featureclass(csv_file)
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
        # count_persons_EsriBonn("DTB", "cnt P Early Weekday", f"{traffic_dir}/early_weekday_*.csv")
        # count_persons("DTB", "cnt P Commute Weekday", f"{traffic_dir}/commute_weekday_*.csv")
        # count_persons_EsriBonn("DTB", "cnt Esri Commmute Weekday", f"{traffic_dir}/commute_weekday_*.csv")
        count_persons_EsriBonn("DTB", "cnt Esri Midnight Weekday", f"{traffic_dir}/midnight_*.csv")

        logging.getLogger("codecarbon").info("")
        logging.getLogger("codecarbon").info("Project summary")
        logging.getLogger("codecarbon").info("===============")
        for summary in get_summary_emissions("log/emissions.csv"):
            logging.getLogger("codecarbon").info(summary)
    except Exception as ex:
        logging.getLogger("codecarbon").error(ex)