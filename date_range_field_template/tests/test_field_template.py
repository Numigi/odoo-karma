# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytz

from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
from odoo import fields, models
from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


def compute_badge_count(records, field_name, date_from, date_to):
    utc_date_from = date_from.astimezone(pytz.utc)
    utc_date_to = date_to.astimezone(pytz.utc)

    badges = records.env['gamification.badge.user'].search([
        ('create_date', '>=', fields.Datetime.to_string(utc_date_from)),
        ('create_date', '<=', fields.Datetime.to_string(utc_date_to)),
        ('user_id', 'in', records.ids),
    ])

    badge_count_by_user = defaultdict(int)

    for badge in badges:
        badge_count_by_user[badge.user_id] += 1

    for user in records:
        user[field_name] = badge_count_by_user[user]


def compute_reached_goal_ratio(records, field_name, date_from, date_to):
    reached_count = _get_reached_goal_count(records, 'reached', date_from, date_to)
    failed_count = _get_reached_goal_count(records, 'failed', date_from, date_to)

    for user in records:
        total = reached_count[user] + failed_count[user]
        user[field_name] = reached_count[user] / total if total else 0


def _get_reached_goal_count(users, state, date_from, date_to):
    goals = users.env['gamification.goal'].search([
        ('start_date', '>=', fields.Date.to_string(date_from)),
        ('start_date', '<=', fields.Date.to_string(date_to)),
        ('user_id', 'in', users.ids),
        ('state', '=', state),
    ])

    goal_count = defaultdict(int)

    for goal in goals:
        goal_count[goal.user_id] += 1

    return goal_count


class ResUsersWithBadgeCount(models.Model):

    _inherit = 'res.users'

    def _register_hook(self):
        super()._register_hook()
        self._register_date_range_field('gamification_badge_count', compute_badge_count)
        self._register_date_range_field('gamification_goal_ratio', compute_reached_goal_ratio)


class TestFieldTemplate(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.ref('base.user_demo')
        cls.badge_1 = cls.env.ref('gamification.badge_good_job')
        cls.badge_2 = cls.env.ref('gamification.badge_problem_solver')
        cls.badge_3 = cls.env.ref('gamification.badge_idea')

        cls.previous_30_days = cls.env['computed.field.date.range'].create({
            'name': 'Previous 30 days',
            'reference': 'previous_30_days',
            'day_min': -30,
            'day_max': -1,
        })

        cls.previous_7_days = cls.env['computed.field.date.range'].create({
            'name': 'Previous 7 days',
            'reference': 'previous_7_days',
            'day_min': -7,
            'day_max': -1,
        })

        cls.range_today = cls.env.ref('date_range_field_template.range_today')

        cls.one_month_ago = datetime.now() - relativedelta(days=30)
        cls.one_week_ago = datetime.now() - relativedelta(days=7)
        cls.now = datetime.now()
        cls.today = datetime(cls.now.year, cls.now.month, cls.now.day)
        cls.today_4_oclock = cls.today + relativedelta(hours=4)

        cls._assign_badge_at_previous_date(cls.env, cls.one_month_ago, cls.badge_1, cls.user)
        cls._assign_badge_at_previous_date(cls.env, cls.one_week_ago, cls.badge_2, cls.user)
        cls._assign_badge_at_previous_date(cls.env, cls.today_4_oclock, cls.badge_3, cls.user)

        cls.definition_1 = cls.env.ref('gamification.definition_base_timezone')
        cls.definition_2 = cls.env.ref('gamification.definition_base_company_data')
        cls._assign_goal(cls.env, cls.one_month_ago, cls.definition_1, cls.user, 'reached')
        cls._assign_goal(cls.env, cls.one_month_ago, cls.definition_2, cls.user, 'reached')
        cls._assign_goal(cls.env, cls.one_week_ago, cls.definition_1, cls.user, 'reached')
        cls._assign_goal(cls.env, cls.one_week_ago, cls.definition_2, cls.user, 'failed')
        cls._assign_goal(cls.env, cls.now, cls.definition_1, cls.user, 'reached')
        cls._assign_goal(cls.env, cls.now, cls.definition_2, cls.user, 'reached')

        cls.template = cls.env['computed.field.template'].create({
            'name': 'Number of Badges Received',
            'model_id': cls.env.ref('base.model_res_users').id,
            'reference': 'gamification_badge_count',
            'field_type': 'integer',
        })

        cls.env['computed.field'].create({
            'template_id': cls.template.id,
            'range_id': cls.previous_30_days.id,
        })

        cls.env['computed.field'].create({
            'template_id': cls.template.id,
            'range_id': cls.previous_7_days.id,
        })

        cls.env['computed.field'].create({
            'template_id': cls.template.id,
            'range_id': cls.range_today.id,
        })

        cls.template_2 = cls.env['computed.field.template'].create({
            'name': 'Ratio of Goals Reached',
            'model_id': cls.env.ref('base.model_res_users').id,
            'reference': 'gamification_goal_ratio',
            'field_type': 'float',
        })

        cls.env['computed.field'].create({
            'template_id': cls.template_2.id,
            'range_id': cls.previous_30_days.id,
        })

        cls.env['computed.field'].create({
            'template_id': cls.template_2.id,
            'range_id': cls.previous_7_days.id,
        })

    @staticmethod
    def _assign_badge_at_previous_date(env, date, badge, user):
        line = env['gamification.badge.user'].create({
            'badge_id': badge.id,
            'user_id': user.id,
        })
        env.cr.execute(
            'UPDATE gamification_badge_user SET create_date = %(date)s '
            'WHERE id = %(line_id)s', {
                'date': date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'line_id': line.id,
            })

    @staticmethod
    def _assign_goal(env, date_, definition, user, state):
        env['gamification.goal'].create({
            'user_id': user.id,
            'definition_id': definition.id,
            'start_date': date_,
            'end_date': date_ + relativedelta(days=30),
            'state': state,
            'target_goal': 0,
        })

    def test_number_of_badges_previous_7_days(self):
        self.assertEqual(self.user.x__gamification_badge_count__previous_7_days, 1)

    def test_number_of_badges_previous_30_days(self):
        self.assertEqual(self.user.x__gamification_badge_count__previous_30_days, 2)

    def test_goal_ratio_previous_7_days(self):
        self.assertAlmostEqual(self.user.x__gamification_goal_ratio__previous_7_days, 0.5, 2)

    def test_goal_ratio_previous_30_days(self):
        self.assertAlmostEqual(self.user.x__gamification_goal_ratio__previous_30_days, 0.75, 2)

    def test_number_of_badges_today(self):
        with freeze_time(self.today):
            self.assertEqual(self.user.x__gamification_badge_count__today, 1)

    def test_number_of_badges_today_with_canada_eastern_tz_plus_3_hours(self):
        """Test that a badge is excluded if created yesterday in the user's perspective.

        When evaluating a field with the Canada/Eastern timezone,
        the time is 4 hours before utc.

        Suppose the current time is 2018-07-30 23:00:00-04:00.

        Then, the current day in the user's perspective is:
            from 2018-07-30 00:00:00-04:00 to 2018-07-30 23:59:99-04:00

        Thus, the current day converted in UTC is:
            from 2018-07-30 04:00:00 to 2018-07-31 03:59:99

        Thus, a badge created on 2018-07-30 03:59:59 UTC, was created yesterday in the
        user's perspective.
        """
        tz = 'Canada/Eastern'

        with freeze_time(self.today + relativedelta(hours=3, minutes=59, seconds=59)):
            self.assertEqual(self.user.with_context(tz=tz).x__gamification_badge_count__today, 0)

    def test_number_of_badges_today_with_canada_eastern_tz_plus_4_hours(self):
        tz = 'Canada/Eastern'

        with freeze_time(self.today + relativedelta(hours=4)):
            self.assertEqual(self.user.with_context(tz=tz).x__gamification_badge_count__today, 1)

    def test_number_of_badges_today_with_canada_eastern_tz_plus_27_hours(self):
        tz = 'Canada/Eastern'

        with freeze_time(self.today + relativedelta(hours=27, minutes=59, seconds=59)):
            self.assertEqual(self.user.with_context(tz=tz).x__gamification_badge_count__today, 1)

    def test_number_of_badges_today_with_canada_eastern_tz_more_then_28_hours(self):
        tz = 'Canada/Eastern'

        with freeze_time(self.today + relativedelta(hours=28)):
            self.assertEqual(self.user.with_context(tz=tz).x__gamification_badge_count__today, 0)

    def test_whenUnlinkComputedFieldEntry_thenRelatedFieldIsUnlinked(self):
        field_entry = self.env['computed.field'].create({
            'template_id': self.template.id,
            'range_id': self.env.ref('date_range_field_template.range_yesterday').id,
        })
        field = field_entry.field_id
        self.assertTrue(field.exists())
        field_entry.unlink()
        self.assertFalse(field.exists())
