# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import pytz
from datetime import datetime
from odoo import fields, models


def compute_karma_field_average(
    records: models.BaseModel,
    field_name: str,
    date_from: datetime,
    date_to: datetime,
    related_model_name: str,
):
    """Compute the average score of a user for filling karma fields."""
    utc_date_from = date_from.astimezone(pytz.utc)
    utc_date_to = date_to.astimezone(pytz.utc)

    records.env.cr.execute(
        """
        SELECT log.create_uid, avg(log.score)
        FROM karma_required_field_log AS log
        WHERE log.create_uid in %(user_ids)s
        AND log.create_date >= %(date_from)s
        AND log.create_date <= %(date_to)s
        AND log.model_id = %(model_id)s
        GROUP BY log.create_uid
        """, {
            'user_ids': tuple(records.ids),
            'date_from': fields.Datetime.to_string(utc_date_from),
            'date_to': fields.Datetime.to_string(utc_date_to),
            'model_id': records.env['ir.model']._get_id(related_model_name),
        })

    result = {r[0]: r[1] for r in records.env.cr.fetchall()}

    for user in records:
        user[field_name] = result.get(user.id) or 0


class ResUsers(models.Model):

    _inherit = 'res.users'

    def _register_hook(self):
        super()._register_hook()
        self._register_date_range_field('karma_field_avg', compute_karma_field_average)
