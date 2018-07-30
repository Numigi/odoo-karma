# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date, datetime

from ..date_range import (
    BasicRelativeDateComputer,
    MonthStartDateComputer,
    MonthEndDateComputer,
    YearStartDateComputer,
    YearEndDateComputer,
    DayStartDateComputer,
    DayEndDateComputer,
)


class TestBasicDateRangeComputer:

    def setup_method(self, method):
        self.today = datetime(2018, 5, 10)
        self.now = datetime(2018, 5, 10, 13, 50, 39, 725000)

    def test_range_in_year_only(self):
        computer = BasicRelativeDateComputer(years=-3)
        assert computer.compute(self.today) == datetime(2015, 5, 10)

    def test_range_in_month_only(self):
        computer = BasicRelativeDateComputer(months=-6)
        assert computer.compute(self.today) == datetime(2017, 11, 10)

    def test_range_in_days_only(self):
        computer = BasicRelativeDateComputer(days=-12)
        assert computer.compute(self.today) == datetime(2018, 4, 28)

    def test_range_in_weeks_only(self):
        computer = BasicRelativeDateComputer(weeks=-2)
        assert computer.compute(self.today) == datetime(2018, 4, 26)

    def test_range_in_month_with_beginning_of_month(self):
        basic_compter = BasicRelativeDateComputer(months=-1)
        computer = MonthStartDateComputer(basic_compter)
        assert computer.compute(self.today) == datetime(2018, 4, 1)

    def test_range_two_months_with_beginning_of_month(self):
        basic_compter = BasicRelativeDateComputer(months=-2)
        computer = MonthStartDateComputer(basic_compter)
        assert computer.compute(self.today) == datetime(2018, 3, 1)

    def test_range_in_month_with_end_of_month(self):
        basic_compter = BasicRelativeDateComputer(months=-1)
        computer = MonthEndDateComputer(basic_compter)
        assert computer.compute(self.today) == datetime(2018, 4, 30)

    def test_range_two_months_with_end_of_month(self):
        basic_compter = BasicRelativeDateComputer(months=-2)
        computer = MonthEndDateComputer(basic_compter)
        assert computer.compute(self.today) == datetime(2018, 3, 31)

    def test_range_in_year_with_beginning_of_year(self):
        basic_compter = BasicRelativeDateComputer(years=-1)
        computer = YearStartDateComputer(basic_compter)
        assert computer.compute(self.today) == datetime(2017, 1, 1)

    def test_range_two_years_with_beginning_of_year(self):
        basic_compter = BasicRelativeDateComputer(years=-2)
        computer = YearStartDateComputer(basic_compter)
        assert computer.compute(self.today) == datetime(2016, 1, 1)

    def test_range_in_year_with_end_of_year(self):
        basic_compter = BasicRelativeDateComputer(years=-1)
        computer = YearEndDateComputer(basic_compter)
        assert computer.compute(self.today) == datetime(2017, 12, 31)

    def test_range_two_years_with_end_of_year(self):
        basic_compter = BasicRelativeDateComputer(years=-2)
        computer = YearEndDateComputer(basic_compter)
        assert computer.compute(self.today) == datetime(2016, 12, 31)

    def test_range_in_year_with_start_of_day(self):
        basic_compter = BasicRelativeDateComputer(years=-1)
        computer = DayStartDateComputer(basic_compter)
        assert computer.compute(self.now) == datetime(2017, 5, 10, 0, 0, 0, 0)

    def test_range_in_year_with_end_of_day(self):
        basic_compter = BasicRelativeDateComputer(years=-1)
        computer = DayEndDateComputer(basic_compter)
        assert computer.compute(self.now) == datetime(2017, 5, 10, 23, 59, 59, 999999)
