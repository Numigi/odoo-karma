# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class KarmaWithNumberOfLines(models.Model):

    _inherit = 'karma'

    @api.model
    def _compute(self, computer, record):
        new_score = super()._compute(computer, record)
        new_score._compute_number_of_evaluated_lines()
        return new_score


class KarmaScoreWithNumberOfLines(models.Model):

    _inherit = 'karma.score'

    number_evaluated_lines = fields.Integer()
    total_number_lines = fields.Integer()

    def _compute_number_of_evaluated_lines(self):
        if self.karma_id.type_ == 'inherited':
            lines = self.inherited_detail_ids
            evaluated_lines = lines.filtered(lambda l: l.child_score_id)
        else:
            lines = self.condition_detail_ids
            evaluated_lines = lines.filtered(lambda l: l.condition_reached)

        self.number_evaluated_lines = len(evaluated_lines)
        self.total_number_lines = len(lines)


class KarmaScoreWithReliability(models.Model):
    """Add the reliability to karma scores.

    The reliability is the ratio between the number of lines evaluated and
    over the total number of lines.

    It is only used for displaying the 2 numbers in the same column instead
    of 2 columns.
    """

    _inherit = 'karma.score'

    reliability = fields.Char(compute='_compute_reliability')

    def _compute_reliability(self):
        for score in self:
            score.reliability = "{evaluated} / {total}".format(
                evaluated=score.number_evaluated_lines or 0,
                total=score.total_number_lines or 0
            )
