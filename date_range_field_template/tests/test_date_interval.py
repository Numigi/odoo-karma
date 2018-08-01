# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytz

from datetime import datetime
from freezegun import freeze_time
from odoo.tests.common import TransactionCase

from ..date_range import (
    get_day_start,
    get_day_end,
    get_week_start,
    get_week_end,
    get_month_start,
    get_month_end,
    get_year_start,
    get_year_end,
)


class TestBasicDateConversionCases:

    def setup_method(self, method):
        self.today = datetime(2018, 5, 10)
        self.now = datetime(2018, 5, 10, 13, 50, 39, 725000)

    def test_get_day_start(self):
        assert get_day_start(self.now) == datetime(2018, 5, 10, 0, 0, 0, 0)

    def test_get_day_end(self):
        assert get_day_end(self.now) == datetime(2018, 5, 10, 23, 59, 59, 999999)

    def test_get_week_start(self):
        assert get_week_start(self.today) == datetime(2018, 5, 6)

    def test_get_week_end(self):
        assert get_week_end(self.today) == datetime(2018, 5, 12, 23, 59, 59, 999999)

    def test_get_month_start(self):
        assert get_month_start(self.today) == datetime(2018, 5, 1)

    def test_get_month_end(self):
        assert get_month_end(self.today) == datetime(2018, 5, 31, 23, 59, 59, 999999)

    def test_get_year_start(self):
        assert get_year_start(self.today) == datetime(2018, 1, 1)

    def test_get_year_end(self):
        assert get_year_end(self.today) == datetime(2018, 12, 31, 23, 59, 59, 999999)


class TestComputedFieldDateRange(TransactionCase):

    def _get_range(self, reference):
        range_ = self.ref('date_range_field_template.range_{ref}'.format(ref=reference))
        return range_.with_context(tz='UTC')

    def test_previous_month_from_february_of_bisextile_year(self):
        range_ = self.env.ref('date_range_field_template.range_previous_month')

        expected_date_min = pytz.utc.localize(datetime(2016, 1, 1))
        expected_date_max = pytz.utc.localize(datetime(2016, 1, 31, 23, 59, 59, 999999))

        with freeze_time(datetime(2016, 2, 29)):
            assert range_.get_date_min() == expected_date_min
            assert range_.get_date_max() == expected_date_max

    def test_previous_month_from_february_of_non_bisextile_year(self):
        range_ = self.env.ref('date_range_field_template.range_previous_month')

        expected_date_min = pytz.utc.localize(datetime(2017, 1, 1))
        expected_date_max = pytz.utc.localize(datetime(2017, 1, 31, 23, 59, 59, 999999))

        with freeze_time(datetime(2017, 2, 28)):
            assert range_.get_date_min() == expected_date_min
            assert range_.get_date_max() == expected_date_max

    def test_previous_year_from_31_december_of_bissextile_year(self):
        range_ = self.env.ref('date_range_field_template.range_previous_year')

        expected_date_min = pytz.utc.localize(datetime(2015, 1, 1))
        expected_date_max = pytz.utc.localize(datetime(2015, 12, 31, 23, 59, 59, 999999))

        with freeze_time(datetime(2016, 12, 31)):
            assert range_.get_date_min() == expected_date_min
            assert range_.get_date_max() == expected_date_max

    def test_previous_year_from_31_december_of_non_bissextile_year(self):
        range_ = self.env.ref('date_range_field_template.range_previous_year')

        expected_date_min = pytz.utc.localize(datetime(2016, 1, 1))
        expected_date_max = pytz.utc.localize(datetime(2016, 12, 31, 23, 59, 59, 999999))

        with freeze_time(datetime(2017, 12, 31)):
            assert range_.get_date_min() == expected_date_min
            assert range_.get_date_max() == expected_date_max

    def test_today_from_3_oclock_in_utc_minus_4(self):
        range_ = self.env.ref('date_range_field_template.range_today')
        tz_string = 'Canada/Eastern'
        tz = pytz.timezone(tz_string)
        expected_date_min = tz.localize(datetime(2018, 5, 9, 0))
        expected_date_max = tz.localize(datetime(2018, 5, 9, 23, 59, 59, 999999))

        with freeze_time(datetime(2018, 5, 10, 3)):
            assert range_.with_context(tz=tz_string).get_date_min() == expected_date_min
            assert range_.with_context(tz=tz_string).get_date_max() == expected_date_max

    def test_today_from_4_oclock_in_utc_minus_4(self):
        range_ = self.env.ref('date_range_field_template.range_today')
        tz_string = 'Canada/Eastern'
        tz = pytz.timezone(tz_string)
        expected_date_min = tz.localize(datetime(2018, 5, 10, 0))
        expected_date_max = tz.localize(datetime(2018, 5, 10, 23, 59, 59, 999999))

        with freeze_time(datetime(2018, 5, 10, 4)):
            assert range_.with_context(tz=tz_string).get_date_min() == expected_date_min
            assert range_.with_context(tz=tz_string).get_date_max() == expected_date_max
