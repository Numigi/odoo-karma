# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytz

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


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
        now = self._get_current_datetime()

        date_min = now + relativedelta(
            years=self.year_min,
            months=self.month_min,
            weeks=self.week_min,
            days=self.day_min,
        )

        if self.week_start:
            date_min = get_week_start(date_min)
        elif self.month_start:
            date_min = get_month_start(date_min)
        elif self.year_start:
            date_min = get_year_start(date_min)
        else:
            date_min = get_day_start(date_min)

        return date_min

    @api.multi
    def get_date_max(self) -> datetime:
        """Get the maximum date of the range relative to the current time."""
        now = self._get_current_datetime()

        date_max = now + relativedelta(
            years=self.year_max,
            months=self.month_max,
            weeks=self.week_max,
            days=self.day_max,
        )

        if self.week_end:
            date_max = get_week_end(date_max)
        elif self.month_end:
            date_max = get_month_end(date_max)
        elif self.year_end:
            date_max = get_year_end(date_max)
        else:
            date_max = get_day_end(date_max)

        return date_max

    def _get_current_datetime(self):
        tz = pytz.timezone(self.env.context.get('tz') or 'UTC')
        return datetime.now(tz)


def get_day_start(date_: datetime) -> datetime:
    """Get the start of the day relative to a given date."""
    return date_ - relativedelta(
        hours=date_.hour,
        minutes=date_.minute,
        seconds=date_.second,
        microseconds=date_.microsecond,
    )


def get_day_end(date_: datetime) -> datetime:
    """Get the end of the day relative to a given date."""
    date_ -= relativedelta(
        hours=date_.hour,
        minutes=date_.minute,
        seconds=date_.second,
        microseconds=date_.microsecond,
    )
    date_ += timedelta(1)
    return date_ - relativedelta(microseconds=1)


def get_week_start(date_: datetime) -> datetime:
    """Get the start of the week relative to a given datetime."""
    first_day = date_ - timedelta(date_.isoweekday())
    return get_day_start(first_day)


def get_week_end(date_: datetime) -> datetime:
    """Get the start of the week relative to a given datetime."""
    last_day = date_ + timedelta(6 - date_.isoweekday())
    return get_day_end(last_day)


def get_month_start(date_: datetime) -> datetime:
    """Get the start of the month relative to a given datetime."""
    first_day = date_ - timedelta(date_.day - 1)
    return get_day_start(first_day)


def get_month_end(date_: datetime) -> datetime:
    """Get the start of the month relative to a given datetime."""
    date_ -= timedelta(date_.day - 1)
    date_ += relativedelta(months=1)
    last_day = date_ - timedelta(1)
    return get_day_end(last_day)


def get_year_start(date_: datetime) -> datetime:
    """Get the start of the year relative to a given datetime."""
    date_ -= timedelta(date_.day - 1)
    first_day = date_ - relativedelta(months=date_.month - 1)
    return get_day_start(first_day)


def get_year_end(date_: datetime) -> datetime:
    """Get the start of the year relative to a given datetime."""
    date_ -= timedelta(date_.day - 1)
    date_ += relativedelta(months=13 - date_.month)
    last_day = date_ - timedelta(1)
    return get_day_end(last_day)
