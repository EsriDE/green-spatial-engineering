import arcpy
import os
from sys import argv

class SpaceTimeCube(object):
    
    def create_space_time_cube(self, feature_class: str, space_time_cube_path: str, time_interval: int, distance_interval: int):
        geodatabase_feature_class = arcpy.ExportFeatures_conversion(feature_class, "trafficFeatureClass")

        projected_feature_class = arcpy.Project_management(in_dataset = geodatabase_feature_class,
                                                           out_dataset = f"{geodatabase_feature_class}_projected_25832",
                                                           out_coor_system = arcpy.SpatialReference(25832))

        # Always convert to an absolute path
        # otherwise relative paths can cause an "ERROR 000210: Cannot create output <value>."
        space_time_cube_filepath = os.path.abspath(os.path.join(space_time_cube_path, "SpaceTimeTrafficCube.nc"))

        space_time_cube = arcpy.CreateSpaceTimeCube_stpm(projected_feature_class, 
                                       output_cube = space_time_cube_filepath, 
                                       time_field ="trip_time",
                                       time_step_interval = f"{time_interval} Minutes",
                                       distance_interval =  f"{distance_interval} Meters",
                                       aggregation_shape_type="HEXAGON_GRID")

        return space_time_cube

    def visualize_space_time_cube(self, space_time_cube_path:str):

        arcpy.VisualizeSpaceTimeCube3D_stpm(in_cube = space_time_cube_path,
                                            cube_variable = "COUNT",
                                            display_theme = "VALUE",
                                            output_features = "SpaceTimeCubeVisualize")


class HotColdSpotsTool(object):

    def create_hot_cold_spots_space_time(self, space_time_cube_path: str, distance_interval: int):
    
        arcpy.stpm.EmergingHotSpotAnalysis(in_cube = space_time_cube_path,
                                           analysis_variable = "COUNT",
                                           output_features = "SpaceTimeCube_EmergingHotSpotAnalysis",
                                           neighborhood_distance =  f"{distance_interval} Meters")

        arcpy.stpm.LocalOutlierAnalysis(in_cube = space_time_cube_path,
                                        analysis_variable = "COUNT",
                                        output_features = "SpaceTimeCube_LocalOutlierAnalysis",
                                        neighborhood_distance =  f"{distance_interval} Meters")
        
    def create_hot_cold_spots_feature_class(self, feature_class: str, distance_interval: int, time_interval: int):

        arcpy.CalculateDensity_gapro(input_layer = feature_class,
                                     out_feature_class = "CalculateDensity",
                                     bin_type = "HEXAGON",
                                     bin_size = f"{distance_interval} Meters",
                                     weight = "UNIFORM",
                                     neighborhood_size = f"{distance_interval * 1.5} Meters",
                                     area_unit_scale_factor = "SQUARE_METERS",
                                     time_step_interval = f"{time_interval} Minutes")
        
        arcpy.FindHotSpots_gapro(point_layer = feature_class,
                                 out_feature_class = "FindHotSpots",
                                 bin_size = f"{distance_interval} Meters",
                                 neighborhood_size = f"{distance_interval * 1.5} Meters",
                                 time_step_interval = f"{time_interval} Minutes")
        
    
class PatternsTool(object):
# ToDO: config.user muss space_time_cube_path, time_interval, distance_interval enthalten 
    def run(self, feature_class, workspace_dir, time_interval=1, distance_interval=200):
        arcpy.env.overwriteOutput = True
        gdb_workspace = f"{workspace_dir}/traffic.gdb"
        if not arcpy.Exists(gdb_workspace):
            gdb_result = arcpy.management.CreateFileGDB(workspace_dir, "traffic")
            arcpy.env.workspace = gdb_result[0]
        else:
            arcpy.env.workspace = gdb_workspace

        # SpaceTimeCube Tool
        space_time_cube_tool = SpaceTimeCube()
        space_time_cube = space_time_cube_tool.create_space_time_cube(feature_class,
                                                                      workspace_dir,
                                                                      time_interval,
                                                                      distance_interval)

        # HotColdSpots Tool
        hot_cold_spots_tool = HotColdSpotsTool()
        hot_cold_spots_tool.create_hot_cold_spots_space_time(space_time_cube,
                                                             distance_interval)
        
        # Layer must have time enabled
        """
        layer_result = arcpy.management.MakeFeatureLayer(feature_class, "traffic_layer")
        traffic_layer = layer_result.getOutput(0)
        traffic_layer.enableTime("trip_time")

        hot_cold_spots_tool.create_hot_cold_spots_feature_class(traffic_layer,
                                                                distance_interval,
                                                                time_interval)
        """
        return space_time_cube
