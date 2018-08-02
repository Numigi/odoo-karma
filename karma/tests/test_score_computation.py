# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest

from odoo.tests.common import SavepointCase


class TestComputedKarmaComputation(SavepointCase):

    @classmethod
    def setUpClass(cls):
        cls.karma = cls.env['karma'].create({
            'name': 'Partner Information',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'description': 'Scores the completeness of the information on the partner.',
        })

        cls.line_1 = cls.env['karma.condition.line'].create({
            'karma_id': cls.karma.id,
        })
