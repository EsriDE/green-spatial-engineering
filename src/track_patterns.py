from codecarbon import track_emissions
from configparser import ConfigParser
from glob import glob
import logging
from patterns.tools import PatternsTool
import os
from traffic.read import read_sqlite_to_featureclass

# config.user anpassen

@track_emissions(project_name="Urban Digital Twin Bonn - Patterns", output_file="log/emissions-patterns.user", offline=True, country_iso_code="USA")
def track_patterns():
    traffic_featureclass = "traffic_data"
    workspace_dir = "/arcgis/home/traffic"
    
    patterns_tool = PatternsTool()
    patterns_tool.run(traffic_featureclass, workspace_dir)



if __name__=="__main__":
    logging.basicConfig()
    logger = logging.getLogger("codecarbon")
    
    try:
        track_patterns()

    except Exception as ex:
        logging.getLogger("codecarbon").error(ex)