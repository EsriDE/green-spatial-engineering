import arcpy
import datetime


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

class MeasureTool(object):
    
    def round_datetime(self, dt):
        #dt = date time
        delta = datetime.timedelta(seconds=5)
        return datetime.datetime.min + round((dt - datetime.datetime.min) / delta) * delta
    
    def create_geometry(self, longitude, latitude):

        point = arcpy.Point(longitude, latitude)
        point_geometry = arcpy.PointGeometry(point, arcpy.SpatialReference(4326))

        return point_geometry

    def measure(self, feature_class):
        
        trip_point_a = Trip("Point A", int, float, float, 0, float, float, float)

        feature_class_column_names = ["trip", "longitude", "latitude", "trip_time", "point_direction", "point_distance", "speed"]
        with arcpy.da.UpdateCursor(feature_class, feature_class_column_names) as cur:

            for row in cur:
                
                trip_point_b = Trip("Point B", row[0], row[1], row[2], self.round_datetime(row[3]), float, float ,float)
                if trip_point_b.trip_id == trip_point_a.trip_id:

                    trip_point_b = self.calculate_distance_speed(trip_point_b, trip_point_a)
                    row[4]=trip_point_b.angle
                    row[5]=trip_point_b.distance
                    row[6]=trip_point_b.speed

                    cur.updateRow(row)

                trip_point_a = Trip("Point A", trip_point_b.trip_id, trip_point_b.long, trip_point_b.lat,
                                    trip_point_b.trip_time, trip_point_b.angle, trip_point_b.distance, trip_point_b.speed)

        return feature_class

    def calculate_distance_speed(self, trip_point_b, trip_point_a):
        current_point = self.create_geometry(trip_point_b.lat, trip_point_b.long)
        last_point = self.create_geometry(trip_point_a.lat, trip_point_a.long)
        trip_point_b.angle, trip_point_b.distance = current_point.angleAndDistanceTo(last_point)
        
        differential_seconds = datetime.timedelta.total_seconds(trip_point_b.trip_time - trip_point_a.trip_time)
        trip_point_b.speed = trip_point_b.distance/differential_seconds * 3.6

        return trip_point_b

    def run(self, feature_class: str, output_feature_class: str):
        # TODO: Implement the add fields for 'speed, point_distance, point_direction'
    
        sorted_feature_class = "memory/traffic_data"
        arcpy.Sort_management(feature_class, sorted_feature_class, [["trip", "ASCENDING"], ["trip_time", "ASCENDING"]])
        feature_class = arcpy.AddFields_management(in_table=sorted_feature_class, field_description=[["point_direction", "DOUBLE", "", "", "0", ""], ["point_distance", "DOUBLE", "", "", "0", ""], ["speed", "DOUBLE", "", "", "0", ""]])

        MeasureTool.measure(feature_class)

        arcpy.CopyFeatures_management(feature_class, output_feature_class)

        