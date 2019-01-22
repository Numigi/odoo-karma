# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import SavepointCase


class TestKarmaScoreWithRecordDisplayName(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.karma_partner = cls.env['karma'].create({
            'name': 'Partner Karma',
            'type_': 'condition',
            'model_id': cls.env.ref('base.model_res_partner').id,
        })

        cls.partner_1 = cls.env.ref('base.res_partner_1')
        cls.partner_2 = cls.env.ref('base.res_partner_2')
        cls.partner_3 = cls.env.ref('base.res_partner_3')

        cls.karma_user = cls.env['karma'].create({
            'name': 'User Karma',
            'type_': 'condition',
            'model_id': cls.env.ref('base.model_res_users').id,
        })

        cls.user_1 = cls.env.ref('base.user_demo')
        cls.user_2 = cls.env.ref('base.user_admin')

        cls.score_1 = cls.env['karma.score'].create({
            'karma_id': cls.karma_partner.id,
            'res_id': cls.partner_1.id,
            'res_model': 'res.partner',
            'score': 0,
        })

        cls.score_2 = cls.env['karma.score'].create({
            'karma_id': cls.karma_partner.id,
            'res_id': cls.partner_2.id,
            'res_model': 'res.partner',
            'score': 0,
        })

        cls.score_3 = cls.env['karma.score'].create({
            'karma_id': cls.karma_partner.id,
            'res_id': cls.partner_3.id,
            'res_model': 'res.partner',
            'score': 0,
        })

        cls.score_4 = cls.env['karma.score'].create({
            'karma_id': cls.karma_partner.id,
            'res_id': cls.user_1.id,
            'res_model': 'res.users',
            'score': 0,
        })

        cls.score_5 = cls.env['karma.score'].create({
            'karma_id': cls.karma_partner.id,
            'res_id': cls.user_2.id,
            'res_model': 'res.users',
            'score': 0,
        })

        cls.scores = (cls.score_1 | cls.score_2 | cls.score_3 | cls.score_4 | cls.score_5)

        cls.details = cls.env['karma.score.inherited.detail']
        for score in cls.scores:
            cls.details |= cls.env['karma.score.inherited.detail'].create({
                'score_id': score.id,
                'res_id': score.res_id,
                'res_model': score.res_model,
            })

    def test_display_name_on_score(self):
        assert self.scores.mapped('record_display_name') == [
            self.partner_1.display_name,
            self.partner_2.display_name,
            self.partner_3.display_name,
            self.user_1.display_name,
            self.user_2.display_name,
        ]

    def test_display_name_on_score_details(self):
        assert self.details.mapped('record_display_name') == [
            self.partner_1.display_name,
            self.partner_2.display_name,
            self.partner_3.display_name,
            self.user_1.display_name,
            self.user_2.display_name,
        ]
