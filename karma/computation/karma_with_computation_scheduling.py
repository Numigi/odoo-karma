# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class KarmaWithComputationScheduling(models.Model):
    """Add cron jobs to karmas."""

    _inherit = 'karma'

    cron_schedule = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ])

    last_cron_date = fields.Date('Previous Cron Date', readonly=True)
    force_next_cron_date = fields.Date('Force Next Cron Date')

    def schedule_computation(self):
        """Plan a queued job for each outdated karma.

        Parent karmas have lower priority over their children karmas.
        """
        all_karmas = self.search([])
        karmas_to_compute = all_karmas.filtered(lambda k: k._should_be_recomputed)
        inherited_karma_delay = self._get_children_depth_delay()

        for karma in karmas_to_compute:
            timedelta_ = karma._get_children_karma_depth() * inherited_karma_delay
            karma.with_delay(eta=timedelta_).compute_all_scores()

    def _get_children_depth_delay(self):
        """Get the delay in minutes per depth of inherited karmas.

        The default value is 10 minutes.

        :rtype: datetime.timedelta
        """
        minutes = int(self.env['ir.config_parameter'].get_param('karma.inherited_karma_delay', 10))
        return timedelta(minutes=minutes)

    def _get_children_karma_depth(self, visited_karmas=None):
        """Get the hierarchy depth of the karma.

        :param visited_karmas: karmas already visited when calling the method recursively.
        :return: the children depth
        """
        if visited_karmas is None:
            visited_karmas = self.env['karma']

        # prevent infinite recursion of inherited karmas
        if self in visited_karmas:
            return 0

        if self.type_ == 'inherited':
            children_depths = [
                l.child_karma_id._get_children_karma_depth(visited_karmas | self)
                for l in self.line_ids
            ]
            max_child_depth = max(children_depths) if children_depths else 0
            return max_child_depth + 1
        else:
            return 1 if self.condition_line_ids else 0

    @property
    def _should_be_recomputed(self):
        is_not_computed_with_cron = not self.cron_schedule
        if is_not_computed_with_cron:
            return False

        next_planned_date = next_date_scheduler.compute(self)
        return next_planned_date <= datetime.now().date()


class NextDateScheduler:
    """Compute the next date for which a karma should be ran."""

    def __init__(self):
        self._timedeltas_per_schedule = {}

    def register_schedule(self, schedule, timedelta_):
        self._timedeltas_per_schedule[schedule] = timedelta_

    def compute(self, karma):
        if karma.force_next_cron_date:
            return fields.Date.from_string(karma.force_next_cron_date)

        if not karma.last_cron_date:
            return datetime.now().date()

        last_cron_date = fields.Date.from_string(karma.last_cron_date)
        timedelta_ = self._timedeltas_per_schedule[karma.cron_schedule]
        return last_cron_date + timedelta_


next_date_scheduler = NextDateScheduler()
next_date_scheduler.register_schedule('daily', timedelta(1))
next_date_scheduler.register_schedule('weekly', timedelta(7))
next_date_scheduler.register_schedule('monthly', relativedelta(months=1))
next_date_scheduler.register_schedule('yearly', relativedelta(years=1))
