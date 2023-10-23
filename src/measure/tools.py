import arcpy
import datetime

class MeasureTool(object):
    
    def round_datetime(dt):
        delta = datetime.timedelta(seconds=5)
        return datetime.datetime.min + round((dt - datetime.datetime.min) / delta) * delta

    def run(self, feature_class: str):
        # TODO: Implement the add fields for 'speed, point_distance, point_direction'

        output_table = arcpy.AddFields_management(in_table=feature_class, field_description=[["point_direction", "DOUBLE", "", "", "0", ""], ["point_distance", "DOUBLE", "", "", "0", ""], ["speed", "DOUBLE", "", "", "0", ""]])


        last_trip_id = int
        last_longitude = float
        last_latitude = float
        last_time = 0

        feature_class_column_names = ["trip", "longitude", "latitude", "trip_time", "point_direction", "point_distance", "speed"]
        with arcpy.da.UpdateCursor(output_table, feature_class_column_names) as cur:

            for row in cur:

                current_trip_id = row[1]
                current_longitude = row[0]
                current_latitude = row[1]
                row[3] = MeasureTool.round_datetime()
                current_time = datetime.datetime.timestamp(row[3])

                if current_trip_id == last_trip_id:
                    current_point = create_point_geometry(current_longitude, current_latitude)
                    last_point = create_point_geometry(last_longitude, last_latitude)
                    angle, distance = current_point.angleAndDistanceTo(last_point)

