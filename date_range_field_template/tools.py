# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def get_technical_field_name(template_reference, range_reference, related_model: str = None):
    """Get a technical field name given the template and date range references.

    :param template_reference: the technical reference of the field template
    :param range_reference: the technical reference of the date range
    :param related_model: the name of the related model to use for the computation
    :returns: the technical name of the field
    """
    technical_name = 'x__{template}'.format(template=template_reference)

    if related_model:
        technical_name += '__{model}'.format(model=related_model.replace('.', '_'))

    technical_name += '__{range}'.format(range=range_reference)

    return technical_name
