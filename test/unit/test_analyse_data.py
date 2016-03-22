"""Tests analysis of data"""
from unittest import TestCase
from mock import MagicMock, patch
import timestring
from toofast.analyse_data import (
    bucket_data, compute_statistics, group_statistics)


def mock_vehicle(speed, datetime=None):
    return {"speed limit": "25", "speed": str(speed), "datetime": datetime}


class AnalyseDataTests(TestCase):
    """Tests analysis of data"""

    def setUp(self):
        """Pre-test setup"""
        pass

    def test_bucket_data(self):
        data = [
            mock_vehicle(20, timestring.Date("1/1/2016 05:00:00")),
            mock_vehicle(20, timestring.Date("1/1/2016 05:01:00")),
            mock_vehicle(20, timestring.Date("1/1/2016 05:02:00")),
            mock_vehicle(20, timestring.Date("1/1/2016 05:14:59")),
            mock_vehicle(30, timestring.Date("1/1/2016 05:15:00")),
            mock_vehicle(30, timestring.Date("1/1/2016 05:16:00")),
            mock_vehicle(30, timestring.Date("1/1/2016 05:17:00")),
            mock_vehicle(30, timestring.Date("1/1/2016 05:29:59"))]
        buckets = bucket_data(data, 15 * 60)
        self.assertEqual(len(buckets), 2)
        bucket_a = [b for k, b in buckets.iteritems() if k.tm_hour == 5 and k.tm_min == 0][0]
        self.assertEqual(len(bucket_a), 4)
        self.assertEqual([val["speed"] for val in bucket_a], ["20", "20", "20", "20"])

    def test_compute_statistics(self):
        buckets = {
            "1": [mock_vehicle(30), mock_vehicle(20)],
            "2": [mock_vehicle(30), mock_vehicle(30)],
            "3": [mock_vehicle(20), mock_vehicle(20)],
            "4": [mock_vehicle(20), mock_vehicle(21),
                  mock_vehicle(22), mock_vehicle(23),
                  mock_vehicle(24), mock_vehicle(25),
                  mock_vehicle(26), mock_vehicle(27),
                  mock_vehicle(28), mock_vehicle(29)],
            "5": []}
        stats = compute_statistics(buckets)
        self.assertAlmostEqual(stats["1"]["max"], 30.0)
        self.assertAlmostEqual(stats["3"]["max"], 20.0)
        self.assertAlmostEqual(stats["1"]["min"], 20.0)
        self.assertAlmostEqual(stats["3"]["min"], 20.0)
        self.assertAlmostEqual(stats["1"]["count_legal"], 1)
        self.assertAlmostEqual(stats["2"]["count_legal"], 0)
        self.assertAlmostEqual(stats["3"]["count_legal"], 2)
        self.assertAlmostEqual(stats["3"]["%legal"], 100.0)
        self.assertAlmostEqual(stats["1"]["diff"], 10.0)
        self.assertAlmostEqual(stats["2"]["diff"], 0.0)
        self.assertAlmostEqual(stats["1"]["mean"], 25.0)
        self.assertAlmostEqual(stats["2"]["mean"], 30.0)
        self.assertAlmostEqual(stats["3"]["mean"], 20.0)
        self.assertAlmostEqual(stats["1"]["count"], 2)
        self.assertAlmostEqual(stats["4"]["85%"], 27.0)
        self.assertAlmostEqual(stats["4"]["99%"], 28.0)
        self.assertAlmostEqual(stats["4"]["50%"], 24.0)
        self.assertAlmostEqual(stats["4"]["limit"], 25.0)
        self.assertIsNone(stats.get("5"))

    def test_group_statistics(self):
        buckets = {
            timestring.Date("2016-01-01 05:00:00").date.timetuple(): [mock_vehicle(20), mock_vehicle(20)],
            timestring.Date("2016-01-01 05:15:00").date.timetuple(): [mock_vehicle(20), mock_vehicle(20)],
            timestring.Date("2016-01-02 05:00:00").date.timetuple(): [mock_vehicle(30), mock_vehicle(30)],
            timestring.Date("2016-01-01 05:15:00").date.timetuple(): [mock_vehicle(25), mock_vehicle(25)]}
        stats = compute_statistics(buckets)
        gstats = group_statistics(stats)
        period1 = gstats["05:00:00"]
        self.assertAlmostEqual(period1["max"], 30.0)
        self.assertAlmostEqual(period1["min"], 20.0)
        self.assertAlmostEqual(period1["count_legal"], 2)
        self.assertAlmostEqual(period1["diff"], 10.0)
        self.assertAlmostEqual(period1["mean"], 25.0)
        self.assertAlmostEqual(period1["count"], 4)
        self.assertAlmostEqual(period1["limit"], 25)
