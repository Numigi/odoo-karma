# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from collections import defaultdict
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class RelatedRecordInfoMixin(models.AbstractModel):
    """Add a reference to the record."""

    _name = 'karma.related.record.info'

    res_id = fields.Integer('Object ID', required=True, index=True)
    res_model = fields.Char('Object Model', required=True)

    record_reference = fields.Char(compute='_compute_record_reference')

    def _compute_record_reference(self):
        for score in self:
            score.record_reference = ','.join([score.res_model, str(score.res_id)])

    record_display_name = fields.Char(compute='_compute_record_display_name')

    def _compute_record_display_name(self):
        """Compute the related record display name.

        The name_get queries are grouped to diminish the number of queries to
        the database.
        """
        scores_by_model = defaultdict(list)

        for score in self:
            scores_by_model[score.res_model].append(score)

        for model, scores in scores_by_model.items():
            related_records = self.env[model].search([
                ('id', 'in', list({r.res_id for r in scores})),
            ])
            display_names = {r[0]: r[1] for r in related_records.name_get()}
            for score in scores:
                score.record_display_name = display_names.get(score.res_id)


class KarmaScore(models.Model):

    _name = 'karma.score'
    _inherit = 'karma.related.record.info'
    _description = 'Karma Score'
    _order = 'id desc'

    karma_id = fields.Many2one('karma', 'Karma', required=True, index=True)
    model_id = fields.Many2one(related='karma_id.model_id', auto_join=True)
    karma_type = fields.Selection(related='karma_id.type_')
    score = fields.Float('Score', digits=dp.get_precision('Karma Score'))
    inherited_detail_ids = fields.One2many(
        'karma.score.inherited.detail', 'score_id', 'Details (Inherited)')

    condition_detail_ids = fields.One2many(
        'karma.score.condition.detail', 'score_id', 'Details (Simple)')


class KarmaScoreInheritedDetail(models.Model):

    _name = 'karma.score.inherited.detail'
    _inherit = 'karma.related.record.info'
    _description = 'Score Detail of Inherited Karma'

    score_id = fields.Many2one('karma.score', 'Score', index=True, ondelete='cascade')
    child_score_id = fields.Many2one('karma.score', 'Score', ondelete='restrict')
    child_score_karma_type = fields.Selection(related="child_score_id.karma_type")

    karma_id = fields.Many2one(related='child_score_id.karma_id')
    score = fields.Float('Score', digits=dp.get_precision('Karma Score'))

    weighting = fields.Float('Weighting', digits=dp.get_precision('Karma Weighting'))
    result = fields.Float('Result', digits=dp.get_precision('Karma Score'))


class KarmaScoreConditionDetail(models.Model):

    _name = 'karma.score.condition.detail'
    _description = 'Score Detail of Simple Karma'

    score_id = fields.Many2one('karma.score', 'Score', index=True, ondelete='cascade')
    condition_id = fields.Many2one('karma.score.condition', 'Condition', required=True)
    field_value = fields.Char()
    condition_reached = fields.Boolean('Condition Reached')
    score = fields.Float('Score', digits=dp.get_precision('Karma Score'))
    result = fields.Float('Result', digits=dp.get_precision('Karma Score'))

    field_id = fields.Many2one(related='condition_id.field_id')
    condition_label = fields.Char(related='condition_id.condition_label')
    condition = fields.Char(related='condition_id.condition')
    result_if_true = fields.Char(related='condition_id.result_if_true')
    result_if_false = fields.Char(related='condition_id.result_if_false')
    weighting = fields.Float(related='condition_id.weighting')


class KarmaScoreCondition(models.Model):

    _name = 'karma.score.condition'
    _description = 'Karma Score Condition'

    karma_id = fields.Many2one('karma', 'Karma', ondelete='cascade')
    field_id = fields.Many2one('ir.model.fields', 'Field', required=True, index=True)
    condition_label = fields.Char(translate=True)
    condition = fields.Char(required=True)
    result_if_true = fields.Char(required=True)
    result_if_false = fields.Char(required=True)
    weighting = fields.Float('Weighting', digits=dp.get_precision('Karma Weighting'))
