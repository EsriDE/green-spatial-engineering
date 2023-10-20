from codecarbon import track_emissions
from configparser import ConfigParser
from glob import glob
import logging
from measure.tools import MeasureTool
import os
from traffic.read import read_sqlite_to_featureclass



@track_emissions(project_name="Urban Digital Twin Bonn - Measure", output_file="log/emissions.user", offline=True, country_iso_code="USA")
def track_measure(traffic_filepath: str):
    traffic_featureclass = read_sqlite_to_featureclass(traffic_file_path, "SELECT * FROM agent_pos LIMIT 10;")
    measure_tool = MeasureTool()
    measure_tool.run(traffic_featureclass)
    #MeasureTool.run(traffic_featureclass)



if __name__=="__main__":
    logging.basicConfig()
    logger = logging.getLogger("codecarbon")
    
    config = ConfigParser()
    config.read("src/config.user")
    
    try:
        traffic_file_path = config["DEFAULT"]["TrafficFilePath"]
        if None is traffic_file_path:
            raise ValueError("Traffic file path not specified!")
        
        track_measure(traffic_file_path)

    except Exception as ex:
        logging.getLogger("codecarbon").error(ex)