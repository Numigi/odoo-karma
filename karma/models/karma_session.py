# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class KarmaSession(models.Model):
    """A session of score computation for a Karma."""

    _name = 'karma.session'
    _order = 'id desc'

    name = fields.Char(compute='_compute_name', store=True)
    karma_id = fields.Many2one('karma', 'Karma', required=True, index=True)
    score_ids = fields.One2many('karma.score', 'session_id', 'Scores')
    number_of_records = fields.Integer()
    start_time = fields.Datetime()
    end_time = fields.Datetime()
    error_log_ids = fields.One2many('karma.error.log', 'session_id', 'Error Logs')

    score_count = fields.Integer(compute='_compute_score_count')
    error_count = fields.Integer(compute='_compute_error_count')

    @api.depends('karma_id', 'start_time')
    def _compute_name(self):
        for record in self:
            record.name = "{karma} ({date})".format(
                karma=record.karma_id.name, date=record.start_time)

    def _compute_score_count(self):
        for record in self:
            record.score_count = len(record.score_ids)

    def _compute_error_count(self):
        for record in self:
            record.error_count = len(record.error_log_ids)


class KarmaScoreWithSession(models.Model):

    _inherit = 'karma.score'

    session_id = fields.Many2one('karma.session', 'Session', index=True)


class KarmaErrorLog(models.Model):
    """Error logs for the Karma computation of a single record."""

    _name = 'karma.error.log'
    _inherit = 'karma.related.record.info'

    karma_id = fields.Many2one('karma', 'Karma', required=True, index=True)
    error_message = fields.Char()
    session_id = fields.Many2one('karma.session', 'Session', index=True, ondelete='cascade')
