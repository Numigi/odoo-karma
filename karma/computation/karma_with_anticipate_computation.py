# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class KarmaWithScoreComputingJob(models.Model):
    """Add cron jobs to karmas."""

    _inherit = 'karma'

    authorize_anticipate_computation = fields.Boolean()

    def run_anticipate_computation(self, record_model, record_id):
        """Compute the score of the record for the given karma.

        :param record_model: the name of the model of the target record.
        :param record_id: the database id of the target record.
        """
        record = self.env[record_model].browse(record_id)
        computer = self._get_score_computer()
        self._compute(computer, record)
