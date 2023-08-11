from datetime import datetime
from traffic.read import read_traffic_as_df
import unittest
from unittest import mock, TestCase


class TestReadTraffic(TestCase):

    def setUp(self):
        self._traffic_content_one = """
            id,trip,person,vehicle_type,distance_crossed,longitude,latitude,trip_time
            1,16980,9987,,69450,7.09401947966322,50.7229459953311,2023-07-07T00:01:00
        """

    def test_read(self):
        file_mock = mock.mock_open(read_data=self._traffic_content_one)
        with mock.patch('builtins.open', file_mock):
            traffic_df = read_traffic_as_df("<ANY>")
            self.assertIsNotNone(traffic_df, "Traffic dataframe must be initialized!")
            self.assertEquals(1, traffic_df.shape[0], "Only one agent entry expected!")
            self.assertIsInstance(traffic_df["trip_time"], datetime, "Trip time must be a datetime!")



if __name__ == "__main__":
    unittest.main()