# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class KarmaWithCompute(models.Model):

    _inherit = 'karma'

    @api.model
    def _compute(self, computer, record):
        """Compute a score for the given record.

        This method serves as a standard hook to add a extra behavior
        before or after the computation of a karma score.

        The objective is to prevent as possible coupling with modules
        that extend karma features from the main computation algorithm.

        The karma computation details are isolated inside the
        ConditionKarmaComputer and InheritedKarmaComputer classes.

        :param computer: the computer object to call
        :param record: the record for which to compute the score
        :return: the new karma score record
        """
        return computer.compute(record)
