import arcpy
from datetime import datetime
from numpy import datetime64, issubdtype
from traffic.calculate import calculate_vehicle_emissions
from traffic.read import read_traffic_as_df, read_traffic_as_sdf, read_traffic_to_featureclass, read_traffic_as_featureclass
from traffic.vehicle import CarSize, DieselCar
import unittest
from unittest import mock, TestCase


class TestReadTraffic(TestCase):

    def setUp(self):
        self._traffic_content_one = """
            id,trip,person,vehicle_type,distance_crossed,longitude,latitude,trip_time
            1,16980,9987,,69450,7.09401947966322,50.7229459953311,2023-07-07T00:01:00
            289645,12245,7195,Bike,11225393,7.08591589604559,50.7453996682822,2023-07-07T07:00:00
        """

    def test_read(self):
        file_mock = mock.mock_open(read_data=self._traffic_content_one)
        with mock.patch('builtins.open', file_mock):
            traffic_df = read_traffic_as_df("<ANY>")
            self.assertIsNotNone(traffic_df, "Traffic dataframe must be initialized!")
            self.assertEquals(2, traffic_df.shape[0], "Two agent entrys expected!")
            self.assertTrue(issubdtype(traffic_df["trip_time"], datetime64), "Trip time must be a datetime!")

    def test_read_spatial(self):
        file_mock = mock.mock_open(read_data=self._traffic_content_one)
        with mock.patch('builtins.open', file_mock):
            traffic_sdf = read_traffic_as_sdf("<ANY>")
            self.assertIsNotNone(traffic_sdf.spatial, "The spatial enabled dataframe must not be none!")

    def test_read_to_featureclass(self):
        file_mock = mock.mock_open(read_data=self._traffic_content_one)
        with mock.patch('builtins.open', file_mock):
            traffic_fc = read_traffic_to_featureclass("traffic")
            self.assertIsNotNone(traffic_fc, "The feature class must not be none!")

    def test_read_as_featureclass(self):
        file_mock = mock.mock_open(read_data=self._traffic_content_one)
        with mock.patch('builtins.open', file_mock):
            traffic_fc = read_traffic_as_featureclass("C:/src/Data.gdb", "traffic")
            self.assertIsNotNone(traffic_fc, "The feature class must not be none!")
            with arcpy.da.SearchCursor(traffic_fc, ["trip_time"]) as search_cursor:
                row = next(search_cursor)
                self.assertLess(0, len(row), "At least one row value was expected!")
                trip_time = row[0]
                self.assertIsInstance(trip_time, datetime, "Trip as datetime was expected!")
                self.assertEquals(1, trip_time.minute, "The trip time is wrong!")


    def test_calculate_traffic_emissions(self):
        file_mock = mock.mock_open(read_data=self._traffic_content_one)
        with mock.patch('builtins.open', file_mock):
            traffic_df = read_traffic_as_df("<ANY>")
            diesel_car = DieselCar(CarSize.LARGE)
            total_emissions = calculate_vehicle_emissions(traffic_df, diesel_car)
            #self.assertNotEquals()



if __name__ == "__main__":
    unittest.main()