"""
Tests of CSV input parsing
"""
from unittest import TestCase
from mock import MagicMock, patch
from toofast.parse_input import (
    extract_file_header,
    read_file_header,
    is_null_vehicle,
    is_valid_vehicle,
    read_vehicle_data,
    read_data_file)


class ParseInputTests(TestCase):
    """Tests of CSV input parsing"""

    def test_extract_file_header_with_data(self):
        row = ["", "", "name[s]", "tester", "", ""]
        self.assertEqual(extract_file_header(row), {"name": "tester"})

    def test_extract_file_header_without_data(self):
        row = ["", "", "blerg", "blergistan", "", ""]
        self.assertEqual(extract_file_header(row), {})

    def test_read_file_header_complete(self):
        csv_reader = []
        csv_reader.append(["", "", "", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "Name[s]", "Daniel K & Julie T", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "Date", "8/10/2015", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "Location", "Rogers Ave & Midwood St", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "Direction", "North", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "Weather", "Sunny", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "Speed Limit", "25", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "", "", "", "", "", "", "", "", "", "", ""])
        my_dict = read_file_header("fakefile", csv_reader)
        self.assertEqual(my_dict.get("direction"), "North")
        self.assertEqual(my_dict.get("filename"), "fakefile")

    def test_read_file_header_incomplete(self):
        csv_reader = []
        csv_reader.append(["", "", "", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "Name[s]", "Daniel K & Julie T", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "Date", "8/10/2015", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "Location", "Rogers Ave & Midwood St", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "Direction", "North", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "Weather", "Sunny", "", "", "", "", "", "", "", "", ""])
        csv_reader.append(["", "", "", "", "", "", "", "", "", "", "", ""])
        self.assertRaises(Exception, read_file_header, "fakefile", csv_reader)

    def test_is_null_vehicle_true(self):
        self.assertTrue(is_null_vehicle({"vehicle": "", "time": "5:00", "speed": "25"}))
        self.assertTrue(is_null_vehicle({"vehicle": "1", "time": "", "speed": "25"}))
        self.assertTrue(is_null_vehicle({"vehicle": "1", "time": "5:00", "speed": ""}))
        self.assertTrue(is_null_vehicle({"vehicle": "Vehicle", "time": "5:00", "speed": "25"}))

    def test_is_null_vehicle_false(self):
        self.assertFalse(is_null_vehicle({"vehicle": "1", "time": "5:00", "speed": "25"}))
        self.assertFalse(is_null_vehicle({"vehicle": "1", "time": "5:00", "speed": "invalid"}))
        self.assertFalse(is_null_vehicle({"vehicle": "1", "time": "invalid", "speed": "25"}))
        self.assertFalse(is_null_vehicle({"vehicle": "invalid", "time": "5:00", "speed": "25"}))

    def test_is_valid_vehicle_true(self):
        self.assertTrue(is_valid_vehicle({"vehicle": "1", "time": "5:00", "speed": "25"}))

    def test_is_valid_vehicle_false(self):
        self.assertFalse(is_valid_vehicle({"vehicle": "", "time": "5:00", "speed": "25"}))
        self.assertFalse(is_valid_vehicle({"vehicle": "blerg", "time": "5:00", "speed": "25"}))
        self.assertFalse(is_valid_vehicle({"vehicle": "1", "time": "5:00", "speed": "blerg"}))
        self.assertFalse(is_valid_vehicle({"vehicle": "1", "time": "5:00", "speed": "2"}))
        self.assertFalse(is_valid_vehicle({"vehicle": "1", "time": "5:00", "speed": "200"}))

    def test_read_vehicle_data(self):
        csv_data = []
        csv_data.append(["", "", "", "", "", "", "", "", "", "", "", ""])
        csv_data.append(["", "Vehicle", "Time", "Speed", "", "Speed", "Vehicle", "Time", "", "", "", ""])
        csv_data.append(["", "1", "5:00", "25", "", "25", "2", "5:01", "", "", "", ""])
        csv_data.append(["", "Vehicle", "Time", "Speed", "", "Speed", "Vehicle", "Time", "", "", "", ""])
        csv_data.append(["", "3", "5:00", "25", "", "25", "4", "5:01", "", "", "", ""])
        csv_reader = MagicMock()
        csv_reader.__iter__ = MagicMock(return_value=iter(csv_data))
        csv_reader.line_num = -1
        file_header = {'date': '2/2/2016'}
        data = read_vehicle_data(file_header, csv_reader)
        self.assertEqual(len(data), 4)
        vehicle_1 = data[0] if data[0].get('vehicle') == '1' else data[1]
        self.assertEqual(vehicle_1['speed'], '25')
        self.assertEqual(vehicle_1['vehicle'], '1')
        self.assertEqual(vehicle_1['time'], '5:00')
        self.assertEqual(vehicle_1['date'], '2/2/2016')

    def test_log_invalid_vehicle(self):
        csv_data = []
        csv_data.append(["", "Vehicle", "Time", "Speed", ""])
        csv_data.append(["", "1", "5:00", "bogus", ""])
        csv_reader = MagicMock()
        csv_reader.__iter__ = MagicMock(return_value=iter(csv_data))
        csv_reader.line_num = 99
        file_header = {'date': '2/2/2016', "filename": "fakename"}
        logging_mock = MagicMock()
        with patch("logging.info", logging_mock):
            read_vehicle_data(file_header, csv_reader)
        self.assertEqual(logging_mock.call_count, 1)
        my_log_str = logging_mock.call_args[0][0]
        self.assertTrue("fakename" in my_log_str)
        self.assertTrue("99" in my_log_str)
        self.assertTrue("bogus" in my_log_str)
