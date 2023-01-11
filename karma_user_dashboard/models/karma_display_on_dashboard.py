# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.addons.karma.models.karma import Karma
from typing import List


class KarmaWithDisplayOnDashboard(models.Model):
    """Add a boolean field on karma to enable displaying it on the user dashboard."""

    _inherit = 'karma'

    display_on_user_dashboard = fields.Boolean()

    @api.model
    def find_scores_to_display_on_user_dashboard(self):
        karmas = self.search([
            ('model_id.model', '=', 'res.users'),
            ('display_on_user_dashboard', '=', True),
        ])

        karmas_matching_user = karmas.filtered(
            lambda k: k.sudo()._domain_matches_record(self.env.user))

        return [read_karma_for_user_dashboard(k) for k in karmas_matching_user]


def read_karma_for_user_dashboard(karma: Karma) -> List[dict]:
    """Read the karma data for using/displaying it in the karma user dashboard.

    If a child karma does not apply for the user, it is discarded
    (The karma can have a domain filter to apply only for specific records).

    :param karma: the parent karma to display on the dashboard.
    :return: the karma record's data
    """
    data = karma.read()[0]

    if karma.type_ == 'inherited':
        child_user_karmas = (
            karma.mapped('line_ids.child_karma_id')
            .filtered(lambda k: k.model == 'res.users')
        )
        child_karmas_matching_user = child_user_karmas.filtered(
            lambda k: k.sudo()._domain_matches_record(karma.env.user))
        data['children'] = child_karmas_matching_user.read()
    else:
        data['children'] = []

    return data
