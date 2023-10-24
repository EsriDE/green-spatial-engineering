import arcpy
import datetime


class Trip(object):

    def __init__(self, name, trip_id, long, lat, trip_time) -> None:
        self.name = name
        self.trip_id = trip_id
        self.long = long
        self.lat = lat
        self.trip_time = trip_time

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
        last_trip_time = 0

        trip_point_a = Trip("Point A", int, float, float, 0)

        feature_class_column_names = ["trip", "longitude", "latitude", "trip_time", "point_direction", "point_distance", "speed"]
        with arcpy.da.UpdateCursor(feature_class, feature_class_column_names) as cur:

            for row in cur:
                
                trip_point_b = Trip("Point B", row[0], row[1], row[2], self.round_datetime(row[3]))

                if trip_point_b.trip_id == trip_point_a.trip_id:

                    angle, distance = self.calculate_distance_speed(trip_point_b, trip_point_a)
                    # if current_trip_id == last_trip_id:

                trip_point_a = Trip("Point A", trip_point_b.trip_id, trip_point_b.long, trip_point_b.lat, trip_point_b.trip_time)

        
        return feature_class

    def calculate_distance_speed(self, trip_point_b, trip_point_a):
        current_point = self.create_geometry(trip_point_b.lat, trip_point_b.long)
        last_point = self.create_geometry(trip_point_a.lat, trip_point_a.long)
        angle, distance = current_point.angleAndDistanceTo(last_point)
        
        differential_seconds = datetime.timedelta.total_seconds(trip_point_b.trip_time - trip_point_a.trip_time)
        speed = distance/differential_seconds * 3.6

        # ggf. Rückgabeparamter in Objekt anlegen und darüber zurückgeben
        return angle, distance, speed
        


    def run(self, feature_class: str, output_feature_class: str):
        # TODO: Implement the add fields for 'speed, point_distance, point_direction'
    
        sorted_feature_class = "memory/traffic_data"
        arcpy.Sort_management(feature_class, sorted_feature_class, [["trip", "ASCENDING"], ["trip_time", "ASCENDING"]])
        feature_class = arcpy.AddFields_management(in_table=sorted_feature_class, field_description=[["point_direction", "DOUBLE", "", "", "0", ""], ["point_distance", "DOUBLE", "", "", "0", ""], ["speed", "DOUBLE", "", "", "0", ""]])

        MeasureTool.measure(feature_class)

        arcpy.CopyFeatures_management(feature_class, output_feature_class)

        