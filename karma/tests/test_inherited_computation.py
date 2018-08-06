# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest

from odoo.tests.common import SavepointCase
from ..computation import InheritedKarmaComputer, ConditionKarmaComputer


class TestComputedKarmaComputation(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner_karma = cls.env['karma'].create({
            'name': 'Partner Information',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'condition_line_ids': [(0, 0, {
                'field_id': cls.env['ir.model.fields'].search([
                    ('model', '=', 'res.partner'),
                    ('name', '=', 'email'),
                ]).id,
                'condition_label': 'Email contains @',
                'condition': "'@' in value",
                'result_if_true': "1",
                'result_if_false': "0",
                'weighting': 10,
            })]
        })

        cls.sale_order_karma = cls.env['karma'].create({
            'name': 'Sale Order Conditions',
            'model_id': cls.env.ref('sale.model_sale_order').id,
            'condition_line_ids': [(0, 0, {
                'field_id': cls.env['ir.model.fields'].search([
                    ('model', '=', 'sale.order'),
                    ('name', '=', 'amount_total'),
                ]).id,
                'condition_label': 'Total amount greater than 1000',
                'condition': "value > 1000",
                'result_if_true': "1",
                'result_if_false': "0",
                'weighting': 20,
            })]
        })

        cls.karma = cls.env['karma'].create({
            'name': 'Global Sale Order Karma',
            'model_id': cls.env.ref('sale.model_sale_order').id,
        })

        cls.line_1 = cls.env['karma.line'].create({
            'karma_id': cls.karma.id,
            'child_karma_id': cls.partner_karma.id,
            'field_id': cls.env['ir.model.fields'].search([
                ('model', '=', 'sale.order'),
                ('name', '=', 'partner_id'),
            ]).id,
            'weighting': 60,
        })

        cls.line_2 = cls.env['karma.line'].create({
            'karma_id': cls.karma.id,
            'child_karma_id': cls.sale_order_karma.id,
            'weighting': 40,
        })

        cls.customer = cls.env['res.partner'].create({
            'name': 'Customer',
            'customer': True,
            'email': 'karma_test@test.com',
        })

        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.customer.id,
            'order_line': [(0, 0, {
                'name': '/',
                'product_id': cls.env.ref('product.service_order_01').id,
                'price_unit': 2000,
                'product_uom_qty': 1,
                'product_uom': cls.env.ref('product.product_uom_unit').id,
            })]
        })

    def setUp(self):
        super().setUp()
        self.computer = InheritedKarmaComputer(self.karma)

    def test_compute_with_no_existing_child_karma_score(self):
        score_line = self.computer.compute(self.order)
        assert len(score_line.inherited_detail_ids) == 2
        assert score_line.score == 0

    def test_compute_with_one_existing_child_karma_score(self):
        ConditionKarmaComputer(self.partner_karma).compute(self.customer)

        score_line = self.computer.compute(self.order)

        partner_weighting = 60 / (60 + 40)
        assert score_line.score == 10 * partner_weighting

    def test_most_recent_child_score_is_used_for_computing_parent_score(self):
        ConditionKarmaComputer(self.partner_karma).compute(self.customer)

        score_line = self.computer.compute(self.order)

        partner_weighting = 60 / (60 + 40)
        assert score_line.score == 10 * partner_weighting

        self.customer.email = False

        ConditionKarmaComputer(self.partner_karma).compute(self.customer)

        score_line_2 = self.computer.compute(self.order)
        assert score_line_2.score == 0

    def test_compute_with_2_children_karma_scores(self):
        ConditionKarmaComputer(self.partner_karma).compute(self.customer)
        ConditionKarmaComputer(self.sale_order_karma).compute(self.order)

        partner_weighting = 60 / (60 + 40)
        order_weighting = 40 / (60 + 40)

        score_line = self.computer.compute(self.order)
        assert score_line.score == 10 * partner_weighting + 20 * order_weighting
