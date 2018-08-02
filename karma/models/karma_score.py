# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class KarmaScore(models.Model):

    _name = 'karma.score'
    _description = 'Karma Score'
    _order = 'id desc'

    karma_id = fields.Many2one('karma', 'Karma', required=True, index=True)
    res_id = fields.Integer('Object ID', required=True, index=True)
    res_model = fields.String('Object Model', required=True)
    score = fields.Float('Score', digits=dp.get_precision('Karma Score'))


class KarmaScoreInheritedDetail(models.Model):

    _name = 'karma.score.inherited.detail'
    _description = 'Score Detail of Inherited Karma'

    score_id = fields.Many2one('karma.score', 'Score', index=True, ondelete='cascade')
    child_score_id = fields.Many2one('karma.score', 'Score', ondelete='restrict')

    karma_id = fields.Many2one('karma', 'Karma', required=True)
    res_id = fields.Integer('Object ID')
    res_model = fields.String('Object Model')
    score = fields.Float('Score', digits=dp.get_precision('Karma Score'))

    weighting = fields.Float('Weighting', digits=dp.get_precision('Karma Weighting'))
    result = fields.Float('Result', digits=dp.get_precision('Karma Score'))


class KarmaScoreConditionDetail(models.Model):

    _name = 'karma.score.condition.detail'
    _description = 'Score Detail of Ad Hoc Karma'

    score_id = fields.Many2one('karma.score', 'Score', index=True, ondelete='cascade')
    condition_id = fields.Many2one('karma.score.condition', 'Condition', required=True)
    field_value = fields.Char()
    condition_fulfilled = fields.Boolean('Condition Fullfiled')
    score = fields.Float('Score', digits=dp.get_precision('Karma Score'))
    result = fields.Float('Result', digits=dp.get_precision('Karma Score'))


class KarmaScoreCondition(models.Model):

    _name = 'karma.score.condition'
    _description = 'Karma Score Condition'

    field_id = fields.Many2one('ir.model.fields', required=True)
    condition = fields.Char(required=True)
    result_if_true = fields.Char(required=True)
    result_if_false = fields.Char(required=True)
    weighting = fields.Float('Weighting', digits=dp.get_precision('Karma Weighting'))
