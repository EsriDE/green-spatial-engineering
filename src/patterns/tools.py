import arcpy
from sys import argv

class SpaceTimeCube(object):
    
    def create_space_time_cube(self, feature_class: str, output_geodatabase: str, space_time_cube_path: str, time_interval: int, distance_interval: int):

        geodatabase_feature_class = arcpy.ExportFeatures_conversion(feature_class, f"{output_geodatabase}/trafficFeatureClass")

        projected_feature_class = arcpy.Project_management(in_dataset = geodatabase_feature_class,
                                                           out_dataset = f"{geodatabase_feature_class}_projected_25832",
                                                           out_coor_system = arcpy.SpatialReference(25832))

        space_time_cube = arcpy.CreateSpaceTimeCube_stpm(projected_feature_class, 
                                       output_cube = f"{space_time_cube_path}/SpaceTimeTrafficCube.nc", 
                                       time_field ="trip_time",
                                       time_step_interval = f"{time_interval} Minutes",
                                       distance_interval =  f"{distance_interval} Meters",
                                       aggregation_shape_type="HEXAGON_GRID")

        return space_time_cube

    def visualize_space_time_cube(self, space_time_cube_path:str, output_geodatabase:str):

        arcpy.VisualizeSpaceTimeCube3D_stpm(in_cube = space_time_cube_path,
                                            cube_variable = "COUNT",
                                            display_theme = "VALUE",
                                            output_features = f"{output_geodatabase}/SpaceTimeCubeVisualize")


class HotColdSpotsTool(object):

    def create_hot_cold_spots_space_time(space_time_cube_path: str, output_geodatabase:str, distance_interval: int):
    
        arcpy.stpm.EmergingHotSpotAnalysis(in_cube = space_time_cube_path,
                                           analysis_variable = "COUNT",
                                           output_features = f"{output_geodatabase}/SpaceTimeCube_EmergingHotSpotAnalysis",
                                           neighborhood_distance =  f"{distance_interval} Meters")

        arcpy.stpm.LocalOutlierAnalysis(in_cube = space_time_cube_path,
                                        analysis_variable = "COUNT",
                                        output_features = f"{output_geodatabase}/SpaceTimeCube_LocalOutlierAnalysis",
                                        neighborhood_distance =  f"{distance_interval} Meters")
        
    def create_hot_cold_spots_feature_class(feature_class: str, output_geodatabase:str, distance_interval: int, time_interval: int):

        # arcpy.FindPointClusters_gapro(input_points = feature_class,
        #                               out_feature_class= f"{output_geodatabase}_PointCluster",
        #                               clustering_method="DBSCAN",
        #                               minimum_points= 100,
        #                               search_distance= f"{distance_interval} Meters",
        #                               use_time="TIME",
        #                               search_duration=f"{time_interval} Minutes")

        arcpy.CalculateDensity_gapro(input_layer = feature_class,
                                     out_feature_class = f"{output_geodatabase}_CalculateDensity",
                                     bin_type = "HEXAGON",
                                     bin_size = f"{distance_interval} Meters",
                                     weight = "UNIFORM",
                                     neighborhood_size = f"{distance_interval * 1.5} Meters",
                                     area_unit_scale_factor = "SQUARE_METERS",
                                     time_step_interval = f"{time_interval} Minutes")
        
        arcpy.FindHotSpots_gapro(point_layer = feature_class,
                                 out_feature_class = f"{output_geodatabase}_FindHotSpots",
                                 bin_size = f"{distance_interval} Meters",
                                 neighborhood_size = f"{distance_interval * 1.5} Meters",
                                 time_step_interval = f"{time_interval} Minutes")
        
