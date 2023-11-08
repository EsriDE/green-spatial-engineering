from codecarbon import track_emissions
from configparser import ConfigParser
from glob import glob
import logging
from measure.tools import MeasureTool
import os
from traffic.read import read_sqlite_to_featureclass, read_sqlite_as_featureclass



@track_emissions(project_name="Urban Digital Twin Bonn - Read SDF", output_file="log/emissions-read.user", offline=True, country_iso_code="USA")
def track_read_sdf(traffic_filepath: str):
    read_sqlite_to_featureclass(traffic_file_path, "SELECT * FROM agent_pos;")

@track_emissions(project_name="Urban Digital Twin Bonn - Read FC", output_file="log/emissions-read.user", offline=True, country_iso_code="USA")
def track_read_fc(traffic_filepath: str):
    read_sqlite_as_featureclass(traffic_file_path, "SELECT * FROM agent_pos;")



if __name__=="__main__":
    logging.basicConfig()
    logger = logging.getLogger("codecarbon")
    
    config = ConfigParser()
    config.read("src/config.user")
    
    try:
        traffic_file_path = config["DEFAULT"]["TrafficFilePath"]
        if None is traffic_file_path:
            raise ValueError("Traffic file path not specified!")
        
        track_read_sdf(traffic_file_path)
        track_read_fc(traffic_file_path)

    except Exception as ex:
        logging.getLogger("codecarbon").error(ex)