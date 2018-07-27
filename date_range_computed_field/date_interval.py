# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import abc

from datetime import date
from dateutil.relativedelta import relativedelta
from typing import Tuple


class AbstractRelativeDateComputer(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def compute(self, reference_date: date) -> date:
        """Compute a date interval given a date of reference.

        The given reference_date parameter is expected to be expressed in the user's timezone.

        The given date is not necessarily the current date.

        :param reference_date: the date from which to compute the interval.
        :return: the date relative to the reference date
        """
        raise NotImplementedError()


class BasicRelativeDateComputer(AbstractRelativeDateComputer):
    """A date interval that computes the dates based on relative time deltas."""

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


class MonthStartDateComputer(AbstractRelativeDateComputer):

    def __init__(self, computer: AbstractRelativeDateComputer):
        self._computer = computer

    def compute(self, reference_date):
        reference_date = self._computer.compute(reference_date)
        return reference_date - relativedelta(days=reference_date.day - 1)


class MonthEndDateComputer(AbstractRelativeDateComputer):

    def __init__(self, computer: AbstractRelativeDateComputer):
        self._computer = computer

    def compute(self, reference_date):
        reference_date = self._computer.compute(reference_date)
        reference_date -= relativedelta(days=reference_date.day - 1)
        reference_date += relativedelta(months=1)
        return reference_date - relativedelta(days=1)


class YearStartDateComputer(AbstractRelativeDateComputer):

    def __init__(self, computer: AbstractRelativeDateComputer):
        self._computer = computer

    def compute(self, reference_date):
        reference_date = self._computer.compute(reference_date)
        reference_date -= relativedelta(days=reference_date.day - 1)
        return reference_date - relativedelta(months=reference_date.month - 1)


class YearEndDateComputer(AbstractRelativeDateComputer):

    def __init__(self, computer: AbstractRelativeDateComputer):
        self._computer = computer

    def compute(self, reference_date):
        reference_date = self._computer.compute(reference_date)
        reference_date -= relativedelta(days=reference_date.day - 1)
        reference_date -= relativedelta(months=reference_date.month - 1)
        reference_date += relativedelta(months=12)
        return reference_date - relativedelta(days=1)
