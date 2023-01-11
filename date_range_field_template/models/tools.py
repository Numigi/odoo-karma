# © 2023 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import Optional


def get_technical_field_name(
    template_reference: str,
    range_reference: str,
    related_model_name: Optional[str] = None
):
    """Get a technical field name given the template and date range references.

    :param template_reference: the technical reference of the field template
    :param range_reference: the technical reference of the date range
    :param related_model_name: the name of the related model to use for the computation
    :returns: the technical name of the field
    """
    technical_name = 'x__{template}'.format(template=template_reference)

    if related_model_name:
        technical_name += '__{model}'.format(model=related_model_name.replace('.', '_'))

    technical_name += '__{range}'.format(range=range_reference)

    return technical_name
