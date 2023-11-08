from codecarbon import track_emissions
from configparser import ConfigParser
from glob import glob
import logging
from track_read import track_read_sdf, track_read_fc
from track_measure import track_measure
from track_patterns import track_patterns



if __name__=="__main__":
    logging.basicConfig()
    logger = logging.getLogger("codecarbon")
    
    config = ConfigParser()
    config.read("src/config.user")
    
    execution_count = 10
    try:
        traffic_file_path = config["DEFAULT"]["TrafficFilePath"]
        if None is traffic_file_path:
            raise ValueError("Traffic file path not specified!")
        
        for _ in range(0, execution_count):
            track_read_sdf(traffic_file_path)
            track_read_fc(traffic_file_path)
            track_measure(traffic_file_path)
            track_patterns()

    except Exception as ex:
        logging.getLogger("codecarbon").error(ex)