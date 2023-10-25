import arcpy
from sys import argv

class SpaceTimeCube(object):
    
    def create_space_time_cube(self, feature_class: str, space_time_cube_path: str, output_geodatabase:str, time_interval: int, distance_interval: int):

        out_dataset="agent_pos_fullData_0_Project"
        out_coor_system = arcpy.SpatialReference(25832)

        projected_feature_class= arcpy.management.Project(feature_class, out_dataset, out_coor_system)

        arcpy.stpm.CreateSpaceTimeCube(projected_feature_class, 
                                       space_time_cube_path, 
                                       time_field="trip_time",
                                       time_step_interval= time_interval + " Minutes",
                                       distance_interval= distance_interval + " Meters",
                                       aggregation_shape_type="HEXAGON_GRID")
        
        arcpy.stpm.VisualizeSpaceTimeCube3D(in_cube=space_time_cube_path, cube_variable="COUNT", display_theme="VALUE", output_features= output_geodatabase + "/SpaceTimeCubeVisualize")


class HotColdSpotsTool(object):
    pass

def hotspot_analysis(agent_pos_fullData_0610_2_="C:\\Users\\thkn.ESRI-DE\\OneDrive - Esri Deutschland + Esri Schweiz\\Documents\\ArcGIS\\Projects\\traffic data\\traffic data.gdb\\agent_pos_fullData_0610"):  # Model

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = False


    # Process: Project (Project) (management)
    agent_pos_fullData_0_Project = "C:\\arcgis\\home\\traffic_simulation\\Hot Cold Spot Analysis - traffic simulation.gdb\\agent_pos_fullData_0_Project"
    arcpy.management.Project(in_dataset=agent_pos_fullData_0610_2_.__str__().format(**locals(),**globals()), out_dataset=agent_pos_fullData_0_Project, out_coor_system="PROJCS[\"ETRS_1989_UTM_Zone_32N\",GEOGCS[\"GCS_ETRS_1989\",DATUM[\"D_ETRS_1989\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",500000.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",9.0],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0.0],UNIT[\"Meter\",1.0]]")

    # Process: Create Space Time Cube By Aggregating Points (Create Space Time Cube By Aggregating Points) (stpm)
    SpaceTimeCube_nc = "C:\\arcgis\\home\\traffic_simulation\\SpaceTimeCube.nc"
    arcpy.stpm.CreateSpaceTimeCube(in_features=agent_pos_fullData_0_Project, output_cube=SpaceTimeCube_nc, time_field="trip_time", time_step_interval="10 Minutes", time_step_alignment="END_TIME", distance_interval="100 Meters", aggregation_shape_type="HEXAGON_GRID")

    # Process: Visualize Space Time Cube in 3D (Visualize Space Time Cube in 3D) (stpm)
    SpaceTimeCube_VisualizeSpaceTimeCube3D1 = "C:\\arcgis\\home\\traffic_simulation\\Hot Cold Spot Analysis - traffic simulation.gdb\\SpaceTimeCube_VisualizeSpaceTimeCube3D1"
    arcpy.stpm.VisualizeSpaceTimeCube3D(in_cube=SpaceTimeCube_nc, cube_variable="COUNT", display_theme="VALUE", output_features=SpaceTimeCube_VisualizeSpaceTimeCube3D1)

if __name__ == '__main__':
    # Global Environment settings
    with arcpy.EnvManager(scratchWorkspace="C:\\arcgis\\home\\traffic_simulation\\Hot Cold Spot Analysis - traffic simulation.gdb", workspace="C:\\arcgis\\home\\traffic_simulation\\Hot Cold Spot Analysis - traffic simulation.gdb"):
        Model(*argv[1:])