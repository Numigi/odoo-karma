# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytest

from odoo.tests.common import SavepointCase
from ..computation import ConditionKarmaComputer


class TestComputedKarmaComputation(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.karma = cls.env['karma'].create({
            'name': 'Partner Information',
            'model_id': cls.env.ref('base.model_res_partner').id,
            'description': 'Scores the completeness of the information on the partner.',
        })

        cls.field_email = cls.env['ir.model.fields'].search([
            ('model', '=', 'res.partner'),
            ('name', '=', 'email'),
        ])

        cls.field_tags = cls.env['ir.model.fields'].search([
            ('model', '=', 'res.partner'),
            ('name', '=', 'category_id'),
        ])

        cls.line_1 = cls.env['karma.condition.line'].create({
            'karma_id': cls.karma.id,
            'field_id': cls.field_email.id,
            'condition_label': 'Email contains @',
            'condition': "'@' in value",
            'result_if_true': "1",
            'result_if_false': "0",
            'weighting': 10,
        })

        cls.line_2 = cls.env['karma.condition.line'].create({
            'karma_id': cls.karma.id,
            'field_id': cls.field_tags.id,
            'condition_label': 'At least 2 partner tags',
            'condition': "len(value) > 1",
            'result_if_true': "len(value) / 2",
            'result_if_false': "0",
            'weighting': 5,
        })

        cls.category_0 = cls.env.ref('base.res_partner_category_0')
        cls.category_1 = cls.env.ref('base.res_partner_category_1')
        cls.category_2 = cls.env.ref('base.res_partner_category_2')

        cls.partner = cls.env['res.partner'].create({
            'name': 'John Doe',
        })

        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Jane Doe',
        })

    def setUp(self):
        super().setUp()
        self.computer = ConditionKarmaComputer(self.karma)

    def test_compute_score_with_email(self):
        self.partner.email = 'test_karma@test.com'
        score_line = self.computer.compute(self.partner)
        assert score_line.score == 10

    def test_compute_score_with_no_category(self):
        score_line = self.computer.compute(self.partner)
        assert score_line.score == 0

    def test_compute_score_with_one_category(self):
        self.partner.category_id = self.category_0
        score_line = self.computer.compute(self.partner)
        assert score_line.score == 0

    def test_compute_score_with_multiple_categories(self):
        self.partner.category_id = self.category_0 | self.category_1 | self.category_2
        number_of_categories = 3

        score_line = self.computer.compute(self.partner)
        assert score_line.score == number_of_categories / 2 * 5

    def test_compute_score_for_multiple_records(self):
        """Test that the same condition computer can be reused for multiple records."""
        self.partner.email = 'test_karma@test.com'
        score_line = self.computer.compute(self.partner)
        assert score_line.score == 10

        self.partner_2.category_id = self.category_0 | self.category_1 | self.category_2
        number_of_categories = 3

        score_line_2 = self.computer.compute(self.partner_2)
        assert score_line_2.score == number_of_categories / 2 * 5

    def test_condition_data_is_copied_only_only_once(self):
        """Test that the condition metadata are copied only once.

        When the conditions are evaluated for more than one record,
        only one `karma.score.condition` record is generated per condition line.

        Each line of `karma.score.condition` is a snapshot of the condition line
        when the computation is done. It can be reused when computing multiple scores.
        """
        score_line = self.computer.compute(self.partner)
        score_line_2 = self.computer.compute(self.partner)

        score_1_conditions = score_line.mapped('condition_detail_ids.condition_id')
        score_2_conditions = score_line_2.mapped('condition_detail_ids.condition_id')
        assert len(score_1_conditions) == 2
        assert score_1_conditions == score_2_conditions

    def test_condition_data_records_are_reused_if_not_changed(self):
        """Test that the condition metadata is reused if the condition did not change."""
        score_line = ConditionKarmaComputer(self.karma).compute(self.partner)
        score_line_2 = ConditionKarmaComputer(self.karma).compute(self.partner)

        score_1_conditions = score_line.mapped('condition_detail_ids.condition_id')
        score_2_conditions = score_line_2.mapped('condition_detail_ids.condition_id')
        assert len(score_1_conditions) == 2
        assert score_1_conditions == score_2_conditions

    def test_condition_data_records_are_not_reused_if_condition_changed(self):
        """Test that the condition metadata is not reused if the condition changed changed."""
        score_line = ConditionKarmaComputer(self.karma).compute(self.partner)

        self.line_2.condition_label = "At least 3 partner tags"
        self.line_2.condition = "len(value) > 2"

        score_line_2 = ConditionKarmaComputer(self.karma).compute(self.partner)

        score_1_conditions = score_line.mapped('condition_detail_ids.condition_id')
        score_2_conditions = score_line_2.mapped('condition_detail_ids.condition_id')

        assert len(score_1_conditions) == 2
        assert len(score_2_conditions) == 2
        assert score_1_conditions != score_2_conditions
