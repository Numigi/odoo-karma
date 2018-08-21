# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class KarmaWithScoreComputingJob(models.Model):
    """Add cron jobs to karmas."""

    _inherit = 'karma'

    compute_on_save = fields.Boolean()

    @api.model
    def compute_score_on_save(self, model, record_id):
        """Compute the scores for the given record.

        :param model: the name of the model of the saved record.
        :param record_id: the database id of the saved record.
        """
        record = self.env[model].browse(record_id)
        karmas = self._find_karmas_triggered_on_save(model, record_id)

        for karma in karmas:
            computer = karma._get_score_computer()
            computer.compute(record)

    def _find_karmas_triggered_on_save(self, model, record_id):
        """Find karma objects that should be triggered on save for the given record."""
        all_karmas = self.search([
            ('model_id.model', '=', model),
            ('compute_on_save', '=', True),
        ])

        def should_be_triggered(karma):
            filter_domain = karma._get_domain()
            found_records = self.env[model].search([('id', '=', record_id)] + filter_domain)
            return found_records.ids == [record_id]

        return all_karmas.filtered(lambda k: should_be_triggered(k))
