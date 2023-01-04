# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.karma.computation import ConditionKarmaComputer
from odoo.addons.karma.tests.common import BasicKarmaTestMixin


class TestComputedKarma(BasicKarmaTestMixin):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_karma.write({'grade_line_ids': [
            (0, 0, {
                'sequence': 0,
                'min_score': 0,
                'max_score': 5,
                'grade': 'ABC',
            }),
            (0, 0, {
                'sequence': 1,
                'min_score': 5,
                'max_score': 10,
                'grade': 'DEF',
            }),
            (0, 0, {
                'sequence': 2,
                'min_score': 10,
                'max_score': 0,
                'grade': 'GHI',
            }),
        ]})

    def _compute(self):
        return self.env['karma']._compute(
            ConditionKarmaComputer(self.partner_karma), self.partner)

    def test_ifScoreIs0_thengradeIsABC(self):
        score_line = self._compute()
        score_line.grade == 'ABC'

    def test_ifScoreIs5_thengradeIsDEF(self):
        self.partner.category_id = self.category  # 5 points
        score_line = self._compute()
        score_line.grade == 'DEF'

    def test_ifScoreIs10_thengradeIsDEF(self):
        self.partner.email = 'test@karma.com'  # 10 points
        score_line = self._compute()
        score_line.grade == 'GHI'

    def test_ifScoreIs15_thengradeIsDEF(self):
        self.partner.category_id = self.category  # 5 points
        self.partner.email = 'test@karma.com'  # 10 points
        score_line = self._compute()
        score_line.grade == 'GHI'
