# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class KarmaSession(models.Model):
    """A session of score computation for a Karma."""

    _name = 'karma.session'

    karma_id = fields.Many2one('karma', 'Karma', required=True, index=True)
    score_ids = fields.One2many('karma.score', 'session_id', 'Scores')
    number_of_records = fields.Integer()
    start_time = fields.Datetime()
    end_time = fields.Datetime()
    error_log_ids = fields.One2many('karma.error.log', 'session_id', 'Error Logs')


class KarmaScoreWithSession(models.Model):

    _inherit = 'karma.score'

    session_id = fields.Many2one('karma.session', 'Session', index=True)


class KarmaErrorLog(models.Model):
    """Error logs for the Karma computation of a single record."""

    _name = 'karma.error.log'

    karma_id = fields.Many2one('karma', 'Karma', required=True, index=True)
    res_id = fields.Integer('Object ID', required=True, index=True)
    res_model = fields.Char('Object Model', required=True)
    error_message = fields.Char()
    session_id = fields.Many2one('karma.session', 'Session', index=True, ondelete='cascade')
