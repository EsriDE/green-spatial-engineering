import arcpy
import datetime

class Point(object):

    def __init__(self, name, long, lat) -> None:
        self.name = name
        self.long = long
        self.lat = lat

    def get_geometry(self):

        return self.long, self.lat

    def get_name(self):
        
        return self.name

class MeasureTool(object):
    
    def round_datetime(self, dt):
        delta = datetime.timedelta(seconds=5)
        return datetime.datetime.min + round((dt - datetime.datetime.min) / delta) * delta
    
    def create_geometry(self, longitude, latitude):

        point = arcpy.Point(longitude, latitude)
        point_geometry = arcpy.PointGeometry(point, arcpy.SpatialReference(4326))

        return point_geometry

    def measure(self, feature_class):

        last_trip_id = int
        last_longitude = float
        last_latitude = float
        last_time = 0

        feature_class_column_names = ["trip", "longitude", "latitude", "trip_time", "point_direction", "point_distance", "speed"]
        with arcpy.da.UpdateCursor(feature_class, feature_class_column_names) as cur:

            for row in cur:

                current_trip_id = row[1]
                current_longitude = row[0]
                current_latitude = row[1]
                row[3] = self.round_datetime()
                current_time = datetime.datetime.timestamp(row[3])
                
                trip_point_b = Point("Point B", current_longitude, current_latitude)
                trip_point_a = Point("Point A", last_longitude, last_latitude)
                angle, distance = self.calculate_distance_speed(trip_point_b, trip_point_a)
                # if current_trip_id == last_trip_id:

        
        return feature_class

    def calculate_distance_speed(self, trip_point_b, trip_point_a):
        current_point = self.create_geometry(trip_point_b.lat, trip_point_b.long)
        last_point = self.create_geometry(trip_point_a.lat, trip_point_a.long)
        angle, distance = current_point.angleAndDistanceTo(last_point)
        
        # speed = 

        # ggf. Rückgabeparamter in Objekt anlegen und darüber zurückgeben
        return angle, distance, speed
        


    def run(self, feature_class: str, output_feature_class: str):
        # TODO: Implement the add fields for 'speed, point_distance, point_direction'
    
        sorted_feature_class = "memory/traffic_data"
        arcpy.Sort_management(feature_class, sorted_feature_class, [["trip", "ASCENDING"], ["trip_time", "ASCENDING"]])
        feature_class = arcpy.AddFields_management(in_table=sorted_feature_class, field_description=[["point_direction", "DOUBLE", "", "", "0", ""], ["point_distance", "DOUBLE", "", "", "0", ""], ["speed", "DOUBLE", "", "", "0", ""]])

        MeasureTool.measure(feature_class)

        arcpy.CopyFeatures_management(feature_class, output_feature_class)

        