import arcpy
import datetime

def convert_timefield(feature_class: str):
    
    feature_class_time_table = arcpy.ConvertTimeField_management(feature_class, 
                                                                input_time_field = "trip_time_old", 
                                                                input_time_format = "yyyy-MM-dd HH:mm:ss;2094", 
                                                                output_time_field = "trip_time")
    
    return feature_class_time_table 

class Trip(object):

    def __init__(self, name, trip_id, long, lat, trip_time, angle, distance, speed) -> None:
        self.name = name
        self.trip_id = trip_id
        self.long = long
        self.lat = lat
        self.trip_time = trip_time
        self.angle = angle
        self.distance = distance
        self.speed = speed
    
    @staticmethod
    def create_empty():
        
        return Trip("empty trip", None, None, None, None, None, None, None)

    def equals(self, other) -> bool:
        if other is None: 
            return False
        
        return self.trip_id == other.trip_id 


class MeasureTool(object):
    
    def change_timefield(self, feature_class: str):
        out_feature_class = arcpy.conversion.ExportFeatures(
            in_features=feature_class,
            out_features="memory/traffic_data_changed_timefield",
            use_field_alias_as_name="NOT_USE_ALIAS",
            field_mapping='id "id" true true false 0 Long 0 0,First,#,traffic_data,id,-1,-1;trip "trip" true true false 0 Long 0 0,First,#,traffic_data,trip,-1,-1;person "person" true true false 0 Long 0 0,First,#,traffic_data,person,-1,-1;vehicle_type "vehicle_type" true true false 8 Text 0 0,First,#,traffic_data,vehicle_type,0,8;distance_crossed "distance_crossed" true true false 0 Long 0 0,First,#,traffic_data,distance_crossed,-1,-1;latitude "latitude" true true false 0 Double 0 0,First,#,traffic_data,latitude,-1,-1;longitude "longitude" true true false 0 Double 0 0,First,#,traffic_data,longitude,-1,-1;trip_time_old "trip_time_old" true true false 38 Text 0 0,First,#,traffic_data,trip_time,0,38',)
        
        return out_feature_class[0]
        
    def create_geometry(self, longitude, latitude):

        point = arcpy.Point(longitude, latitude)
        point_geometry = arcpy.PointGeometry(point, arcpy.SpatialReference(4326))

        return point_geometry

    def measure(self, feature_class):
        
        trip_point_a = Trip.create_empty()

        feature_class_column_names = ["trip", "longitude", "latitude", "trip_time", "trip_time_old", "point_direction", "point_distance", "speed"]
        with arcpy.da.UpdateCursor(feature_class, feature_class_column_names) as cur:

            for row in cur:
                
                timestamp_string = row[4]
                
                format_string = "%Y-%m-%dT%H:%M:%S"
                datetime_object = datetime.datetime.strptime(timestamp_string, format_string)
                row[3] = datetime.datetime.fromtimestamp(datetime.datetime.timestamp(datetime_object) - 3600)
                
                trip_point_b = Trip("Point B", row[0], row[1], row[2], row[3], float, float ,float)
                if trip_point_b.equals(trip_point_a):

                    trip_point_b = self.calculate_distance_speed(trip_point_b, trip_point_a)
                    row[5]=trip_point_b.angle
                    row[6]=trip_point_b.distance
                    row[7]=trip_point_b.speed

                cur.updateRow(row)

                trip_point_a = Trip("Point A", trip_point_b.trip_id, trip_point_b.long, trip_point_b.lat,
                                    trip_point_b.trip_time, trip_point_b.angle, trip_point_b.distance, trip_point_b.speed)

        return feature_class

    def calculate_distance_speed(self, trip_point_b, trip_point_a):
        current_point = self.create_geometry(trip_point_b.lat, trip_point_b.long)
        last_point = self.create_geometry(trip_point_a.lat, trip_point_a.long)
        trip_point_b.angle, trip_point_b.distance = current_point.angleAndDistanceTo(last_point)
        
        differential_seconds = datetime.timedelta.total_seconds(trip_point_b.trip_time - trip_point_a.trip_time)

        if trip_point_b.distance == 0:
            trip_point_b.speed = 0
        else:
            trip_point_b.speed = trip_point_b.distance/differential_seconds * 3.6

        trip_point_b.distance = round(trip_point_b.distance, 2)

        return trip_point_b

    def run(self, feature_class: str, workspace_dir: str):
        arcpy.env.overwriteOutput = True
        gdb_workspace = f"{workspace_dir}/traffic.gdb"
        if not arcpy.Exists(gdb_workspace):
            gdb_result = arcpy.management.CreateFileGDB(workspace_dir, "traffic")
            arcpy.env.workspace = gdb_result[0]
        else:
            arcpy.env.workspace = gdb_workspace

        feature_class = self.change_timefield(feature_class)

        arcpy.Sort_management(feature_class, "traffic_data", [["trip", "ASCENDING"], ["trip_time_old", "ASCENDING"]])
        feature_class = arcpy.AddFields_management(in_table="traffic_data", field_description=[["trip_time", "DATE"],["point_direction", "DOUBLE", "", "", "0", ""], ["point_distance", "DOUBLE", "", "", "0", ""], ["speed", "DOUBLE", "", "", "0", ""]])

        self.measure(feature_class)
        arcpy.DeleteField_management(feature_class, drop_field=["trip_time_old", "ORIG_FID"])
        return feature_class
