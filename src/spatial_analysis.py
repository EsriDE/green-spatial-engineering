from traffic.read import read_sqlite_to_featureclass
from measure.tools import MeasureTool
from patterns.tools import HotColdSpotsTool, SpaceTimeCube


def run(db_filepath: str, select_statement: str, space_time_cube_path: str, time_interval: int, distance_interval: int, output_geodatabase: str, x_column: str='longitude', y_column: str='latitude'):

    feature_class= read_sqlite_to_featureclass(db_filepath, "SELECT * from agent_pos LIMIT 10;")

    measure_tool = MeasureTool()
    feature_class = measure_tool.run(feature_class)

    space_time_cube = SpaceTimeCube()
    space_time_cube.create_space_time_cube(feature_class, space_time_cube_path, time_interval=15, distance_interval=100)
    space_time_cube.visualize_space_time_cube(space_time_cube_path, output_geodatabase)

    hot_cold_spots = HotColdSpotsTool()
    hot_cold_spots.create_hot_cold_spots_feature_class()

    pass