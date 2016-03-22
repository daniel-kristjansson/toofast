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
        stats = {
            timestring.Date("1/1/2016 1:00:00"): {"s1": 121212},
            timestring.Date("1/1/2016 1:01:00"): {"s2": 232323, "_fun": "baddata"}}
        out = StringIO.StringIO()
        output_csv(out, stats)
        self.outstr = out.getvalue()
        out.close()

    def test_output_csv_no_stats_no_exception(self):
        output_csv(None, {})

    def test_output_csv_outputs_keys_in_order(self):
        assert "when,s1,s2" in self.outstr

    def test_output_csv_outputs_values_in_place(self):
        assert ",121212," in self.outstr
        assert ",,232323" in self.outstr

    def test_output_csv_ignores_underscore_data(self):
        assert "baddata" not in self.outstr
