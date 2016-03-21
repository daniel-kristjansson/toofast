"""Tests output of statistics"""
from unittest import TestCase
from mock import MagicMock, patch
import timestring
import StringIO
from toofast.output_statistics import output_csv


class OutputStatisticsTests(TestCase):
    """Tests output of statistics"""

    def setUp(self):
        """Pre-test setup"""
        pass

    def test_output_csv_no_stats_no_exception(self):
        output_csv(None, {})

    def test_output_csv_outputs_data(self):
        stats = {
            timestring.Date("1/1/2016 1:00:00"): {"s": 121212},
            timestring.Date("1/1/2016 1:01:00"): {"s": 232323}}
        out = StringIO.StringIO()
        out.write("write something\n")
        output_csv(out, stats)
        assert "121212" in out.getvalue()
        assert "232323" in out.getvalue()
        out.close()
