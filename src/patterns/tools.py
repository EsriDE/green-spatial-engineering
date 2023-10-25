import arcpy
from sys import argv

class SpaceTimeCube(object):
    
    def create_space_time_cube(feature_class: str, space_time_cube_path: str, time_interval: int, distance_interval: int):

        #TODO: Name für Feature Class anlegen mit Pfad etc.
        projected_feature_class="agent_pos_fullData_0_Project"
        out_coor_system = arcpy.SpatialReference(25832)

        arcpy.management.Project(feature_class, projected_feature_class, out_coor_system)

        arcpy.stpm.CreateSpaceTimeCube(projected_feature_class, 
                                       space_time_cube_path, 
                                       time_field ="trip_time",
                                       time_step_interval =  f"{time_interval} Minutes",
                                       distance_interval =  f"{distance_interval} Meters",
                                       aggregation_shape_type="HEXAGON_GRID")
        
        return space_time_cube_path

    def visualize_space_time_cube(self, space_time_cube_path:str, output_geodatabase:str):

        arcpy.stpm.VisualizeSpaceTimeCube3D(in_cube = space_time_cube_path,
                                            cube_variable = "COUNT",
                                            display_theme = "VALUE",
                                            output_features = output_geodatabase + "/SpaceTimeCubeVisualize")


class HotColdSpotsTool(object):

    def create_hot_cold_spots(self, feature_class: str, space_time_cube_path: str, output_geodatabase:str, time_interval: int, distance_interval: int):
    
        arcpy.stpm.EmergingHotSpotAnalysis(in_cube = space_time_cube_path,
                                           analysis_variable = "COUNT",
                                           output_features = output_geodatabase + "/SpaceTimeCube_EmergingHotSpotAnalysis",
                                           neighborhood_distance =  f"{distance_interval} Meters")

        arcpy.stpm.LocalOutlierAnalysis(in_cube = space_time_cube_path,
                                        analysis_variable = "COUNT",
                                        output_features = output_geodatabase + "/SpaceTimeCube_LocalOutlierAnalysis",
                                        neighborhood_distance =  f"{distance_interval} Meters")