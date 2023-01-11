# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from .common import BasicKarmaTestMixin
from odoo.addons.karma.computation import (
    ConditionKarmaComputer,
    InheritedKarmaComputer,
)


class TestComputedKarma(BasicKarmaTestMixin):

    def _compute(self):
        return self.env['karma']._compute(
            ConditionKarmaComputer(self.partner_karma), self.partner)

    def test_ifNoFieldFilled_thenOneEvaluatedLine(self):
        score_line = self._compute()
        assert score_line.number_evaluated_lines == 0
        assert score_line.total_number_lines == 2

    def test_ifEmailFilled_thenOneEvaluatedLine(self):
        self.partner.email = 'test_karma@test.com'
        score_line = self._compute()
        assert score_line.number_evaluated_lines == 1
        assert score_line.total_number_lines == 2

    def test_ifEmailAndCategoryFilled_thenOneEvaluatedLine(self):
        self.partner.email = 'test_karma@test.com'
        self.partner.category_id = self.category
        score_line = self._compute()
        assert score_line.number_evaluated_lines == 2
        assert score_line.total_number_lines == 2


class TestInheritedKarma(BasicKarmaTestMixin):

    def _compute(self):
        return self.env['karma']._compute(
            InheritedKarmaComputer(self.inherited_so_karma), self.order)

    def test_number_of_evaluated_lines_with_no_child_score(self):
        score_line = self._compute()
        assert score_line.number_evaluated_lines == 0
        assert score_line.total_number_lines == 2

    def test_number_of_evaluated_lines_with_1_child_score(self):
        ConditionKarmaComputer(self.partner_karma).compute(self.partner)

        score_line = self._compute()
        assert score_line.number_evaluated_lines == 1
        assert score_line.total_number_lines == 2

    def test_number_of_evaluated_lines_with_2_child_scores(self):
        ConditionKarmaComputer(self.partner_karma).compute(self.partner)
        ConditionKarmaComputer(self.sale_order_karma).compute(self.order)

        score_line = self._compute()
        assert score_line.number_evaluated_lines == 2
        assert score_line.total_number_lines == 2
