# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytz

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class ComputedFieldDateRange(models.Model):
    """Date ranges for computed fields.

    The methods get_date_min and get_date_max return
    datetimes in the timezone of the context (UTC if none given).

    The combined result of the 2 methods is a datetime range.

    The range depends on the user's timezone.

    If the given current datetime is 2018-05-31 23:00:00 in Canada/Eastern,
    the expected datetime range that represents the current month is

    2018-05-01 00:00:00 to 2018-05-31 23:59:59 and 999999 microseconds
    in Canada/Eastern

    This is equivalent to the following range in UTC.

    2018-05-01 04:00:00 to 2018-06-01 03:59:59 and 999999 microseconds
    """

    _name = 'computed.field.date.range'
    _description = 'Date Range For Computed Fields'

    name = fields.Char(required=True, translate=True)
    reference = fields.Char(required=True)
    active = fields.Boolean(default=True)

    enable_date_min = fields.Boolean(default=True)
    enable_date_max = fields.Boolean(default=True)

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
        if not self.enable_date_min:
            return None

        date_min = self._get_current_datetime()

        if self.year_min:
            date_min += relativedelta(years=self.year_min)

        if self.year_start:
            date_min = get_first_day_of_year(date_min)

        if self.month_min:
            date_min += relativedelta(months=self.month_min)

        if self.month_start:
            date_min = get_first_day_of_month(date_min)

        if self.week_min:
            date_min += relativedelta(weeks=self.week_min)

        if self.week_start:
            date_min = get_first_day_of_week(date_min)

        if self.day_min:
            date_min += timedelta(self.day_min)

        return get_day_start(date_min)

    @api.multi
    def get_date_max(self) -> datetime:
        """Get the maximum date of the range relative to the current time."""
        if not self.enable_date_max:
            return None

        date_max = self._get_current_datetime()

        if self.year_max:
            date_max += relativedelta(years=self.year_max)

        if self.year_end:
            date_max = get_last_day_of_year(date_max)

        if self.month_max:
            date_max += relativedelta(months=self.month_max)

        if self.month_end:
            date_max = get_last_day_of_month(date_max)

        if self.week_max:
            date_max += relativedelta(weeks=self.week_max)

        if self.week_end:
            date_max = get_last_day_of_week(date_max)

        if self.day_max:
            date_max += timedelta(self.day_max)

        return get_day_end(date_max)

    def _get_current_datetime(self):
        tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
        return datetime.now(tz)


def get_day_start(datetime_: datetime) -> datetime:
    """Get the start of the day relative to a given date."""
    return datetime_ - relativedelta(
        hours=datetime_.hour,
        minutes=datetime_.minute,
        seconds=datetime_.second,
        microseconds=datetime_.microsecond,
    )


def get_day_end(datetime_: datetime) -> datetime:
    """Get the end of the day relative to a given date."""
    datetime_ -= relativedelta(
        hours=datetime_.hour,
        minutes=datetime_.minute,
        seconds=datetime_.second,
        microseconds=datetime_.microsecond,
    )
    datetime_ += timedelta(1)
    return datetime_ - relativedelta(microseconds=1)


def get_first_day_of_week(datetime_: datetime) -> datetime:
    """Get the start of the week relative to a given datetime."""
    return datetime_ - timedelta(datetime_.isoweekday())


def get_last_day_of_week(datetime_: datetime) -> datetime:
    """Get the start of the week relative to a given datetime."""
    return datetime_ + timedelta(6 - datetime_.isoweekday())


def get_first_day_of_month(datetime_: datetime) -> datetime:
    """Get the start of the month relative to a given datetime."""
    return datetime_ - timedelta(datetime_.day - 1)


def get_last_day_of_month(datetime_: datetime) -> datetime:
    """Get the start of the month relative to a given datetime."""
    datetime_ -= timedelta(datetime_.day - 1)
    datetime_ += relativedelta(months=1)
    return datetime_ - timedelta(1)


def get_first_day_of_year(datetime_: datetime) -> datetime:
    """Get the start of the year relative to a given datetime."""
    datetime_ -= timedelta(datetime_.day - 1)
    return datetime_ - relativedelta(months=datetime_.month - 1)


def get_last_day_of_year(datetime_: datetime) -> datetime:
    """Get the start of the year relative to a given datetime."""
    datetime_ -= timedelta(datetime_.day - 1)
    datetime_ += relativedelta(months=13 - datetime_.month)
    return datetime_ - timedelta(1)
