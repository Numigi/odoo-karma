# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import abc
import pytz

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from typing import Tuple


class AbstractRelativeDateComputer(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def compute(self, reference_date: datetime) -> datetime:
        """Compute a date range given a date of reference.

        The given reference_date parameter is expected to be expressed in the user's timezone.

        The given date is not necessarily the current date.

        :param reference_date: the date from which to compute the range.
        :return: the date relative to the reference date
        """
        raise NotImplementedError()


class BasicRelativeDateComputer(AbstractRelativeDateComputer):
    """A date range that computes the dates based on relative time deltas."""

    def __init__(
        self, years: int = 0, months: int = 0, weeks: int = 0, days: int = 0,
    ):
        self._years = years
        self._months = months
        self._weeks = weeks
        self._days = days

    def compute(self, reference_date):
        if self._years:
            reference_date += relativedelta(years=self._years)

        if self._months:
            reference_date += relativedelta(months=self._months)

        if self._weeks:
            reference_date += relativedelta(weeks=self._weeks)

        if self._days:
            reference_date += relativedelta(days=self._days)

        return reference_date


class DateComputerDecorator(AbstractRelativeDateComputer):

    def __init__(self, computer: AbstractRelativeDateComputer):
        self._computer = computer


class WeekStartDateComputer(DateComputerDecorator):

    def compute(self, reference_date):
        reference_date = self._computer.compute(reference_date)
        return reference_date - relativedelta(days=reference_date.isoweekday())


class WeekEndDateComputer(DateComputerDecorator):

    def compute(self, reference_date):
        reference_date = self._computer.compute(reference_date)
        reference_date -= relativedelta(days=reference_date.isoweekday())
        reference_date += relativedelta(weeks=1)
        return reference_date - relativedelta(days=1)


class MonthStartDateComputer(DateComputerDecorator):

    def compute(self, reference_date):
        reference_date = self._computer.compute(reference_date)
        return reference_date - relativedelta(days=reference_date.day - 1)


class MonthEndDateComputer(DateComputerDecorator):

    def compute(self, reference_date):
        reference_date = self._computer.compute(reference_date)
        reference_date -= relativedelta(days=reference_date.day - 1)
        reference_date += relativedelta(months=1)
        return reference_date - relativedelta(days=1)


class YearStartDateComputer(DateComputerDecorator):

    def compute(self, reference_date):
        reference_date = self._computer.compute(reference_date)
        reference_date -= relativedelta(days=reference_date.day - 1)
        return reference_date - relativedelta(months=reference_date.month - 1)


class YearEndDateComputer(DateComputerDecorator):

    def compute(self, reference_date):
        reference_date = self._computer.compute(reference_date)
        reference_date -= relativedelta(days=reference_date.day - 1)
        reference_date -= relativedelta(months=reference_date.month - 1)
        reference_date += relativedelta(months=12)
        return reference_date - relativedelta(days=1)


class DayStartDateComputer(DateComputerDecorator):

    def compute(self, reference_date):
        reference_date = self._computer.compute(reference_date)
        return reference_date - relativedelta(
            hours=reference_date.hour,
            minutes=reference_date.minute,
            seconds=reference_date.second,
            microseconds=reference_date.microsecond,
        )


class DayEndDateComputer(DateComputerDecorator):

    def compute(self, reference_date):
        reference_date = self._computer.compute(reference_date)
        reference_date -= relativedelta(
            hours=reference_date.hour,
            minutes=reference_date.minute,
            seconds=reference_date.second,
            microseconds=reference_date.microsecond,
        )
        reference_date += relativedelta(days=1)
        return reference_date - relativedelta(microseconds=1)


class ComputedFieldDateRange(models.Model):

    _name = 'computed.field.date.range'
    _description = 'Date Range For Computed Fields'

    name = fields.Char(required=True, translate=True)
    reference = fields.Char(required=True)
    active = fields.Boolean(default=True)

    day_min = fields.Integer()
    week_min = fields.Integer()
    month_min = fields.Integer()
    year_min = fields.Integer()

    day_max = fields.Integer()
    week_max = fields.Integer()
    month_max = fields.Integer()
    year_max = fields.Integer()

    week_start = fields.Boolean('Start on previous Sunday')
    week_end = fields.Boolean('End on the following Saturday')
    month_start = fields.Boolean('Start on first day of month')
    month_end = fields.Boolean('End on last day of month')
    year_start = fields.Boolean('Start on January 1rst')
    year_end = fields.Boolean('End on December 31th')

    _sql_constraints = [
        ('unique_reference', 'unique(reference)',
         'The reference of a date range must be unique.'),
    ]

    @api.multi
    def get_date_min(self) -> datetime:
        """Get the minimum date of the range relative to the current time."""
        computer = BasicRelativeDateComputer(
            years=self.year_min, months=self.month_min, weeks=self.week_min, days=self.day_min,
        )

        if self.week_start:
            computer = WeekStartDateComputer(computer)

        elif self.month_start:
            computer = MonthStartDateComputer(computer)

        elif self.year_start:
            computer = YearStartDateComputer(computer)

        computer = DayStartDateComputer(computer)

        return computer.compute(self._get_current_datetime())

    @api.multi
    def get_date_max(self) -> datetime:
        """Get the maximum date of the range relative to the current time."""
        computer = BasicRelativeDateComputer(
            years=self.year_max, months=self.month_max, weeks=self.week_max, days=self.day_max,
        )

        if self.week_end:
            computer = WeekEndDateComputer(computer)

        elif self.month_end:
            computer = MonthEndDateComputer(computer)

        elif self.year_end:
            computer = YearEndDateComputer(computer)

        computer = DayEndDateComputer(computer)

        return computer.compute(self._get_current_datetime())

    def _get_current_datetime(self):
        tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
        return datetime.now(tz)
