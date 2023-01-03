# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class KarmaWithgrades(models.Model):

    _inherit = 'karma'

    grade_line_ids = fields.One2many('karma.grade.range', 'karma_id', 'Grade Ranges')

    @api.model
    def _compute(self, computer, record):
        new_score = super()._compute(computer, record)
        new_score._compute_grade()
        return new_score


class KarmaGradeRange(models.Model):

    _name = 'karma.grade.range'
    _description = 'Karma Grade Range'
    _order = 'sequence'

    karma_id = fields.Many2one('karma', 'Karma', required=True, ondelete='cascade')
    sequence = fields.Integer()
    min_score = fields.Float('Lower Boundary', digits=dp.get_precision('Karma Score'))
    max_score = fields.Float('Upper Boundary', digits=dp.get_precision('Karma Score'))
    grade = fields.Char(required=True, translate=True)


class KarmaScoreWithGrade(models.Model):

    _inherit = 'karma.score'

    grade = fields.Char()

    def _compute_grade(self):
        matching_grade_line = next((
            l for l in self.karma_id.grade_line_ids
            if (not l.min_score or l.min_score <= self.score) and
               (not l.max_score or self.score < l.max_score)
        ), None)

        if matching_grade_line is not None:
            self.grade = matching_grade_line.grade
