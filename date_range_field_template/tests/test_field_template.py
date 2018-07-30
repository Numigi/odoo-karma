# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models
from odoo.tests import common
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from ..field_template import FieldTemplate


class GamificationBadgeCount(FieldTemplate):

    def compute(self, records, field_name, date_from, date_to):
        badges = records.env['gamification.badge.user'].search([
            ('create_date', '>=', fields.Date.to_string(date_from)),
            ('create_date', '<=', fields.Date.to_string(date_to)),
            ('user_id', 'in', records.ids),
        ])

        badge_count_by_user = defaultdict(int)

        for badge in badges:
            badge_count_by_user[badge.user_id] += 1

        for user in records:
            user[field_name] = badge_count_by_user[user]


class ResUsersWithBadgeCount(models.Model):

    _inherit = 'res.users'

    def _register_hook(self):
        super()._register_hook()
        self._register_date_range_field('gamification_badge_count', GamificationBadgeCount())


class TestFieldTemplate(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.env.ref('base.user_demo')
        cls.badge_1 = cls.env.ref('gamification.badge_good_job')
        cls.badge_2 = cls.env.ref('gamification.badge_problem_solver')
        cls.badge_3 = cls.env.ref('gamification.badge_idea')

        cls.one_month_ago = datetime.now() - relativedelta(months=1)
        cls.one_week_ago = datetime.now() - relativedelta(weeks=1)
        cls.now = datetime.now()

        cls._assign_badge_at_previous_date(cls.env, cls.one_month_ago, cls.badge_1, cls.user)
        cls._assign_badge_at_previous_date(cls.env, cls.one_week_ago, cls.badge_2, cls.user)
        cls._assign_badge_at_previous_date(cls.env, cls.now, cls.badge_3, cls.user)

        cls.template = cls.env['computed.field.template'].create({
            'name': 'Number of Badges Received',
            'model_id': cls.env.ref('base.model_res_users').id,
            'reference': 'gamification_badge_count',
            'field_type': 'integer',
        })

        cls.env['computed.field'].create({
            'template_id': cls.template.id,
            'range_id': cls.env.ref('date_range_field_template.range_previous_week').id,
        })

        cls.env['computed.field'].create({
            'template_id': cls.template.id,
            'range_id': cls.env.ref('date_range_field_template.range_current_month').id,
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

    def test_number_of_badges_previous_week(self):
        self.assertEqual(self.user.x__gamification_badge_count__previous_week, 1)

    def test_number_of_badges_current_month(self):
        self.assertEqual(self.user.x__gamification_badge_count__current_month, 2)
