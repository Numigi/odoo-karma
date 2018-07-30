# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def get_technical_field_name(template_reference, range_reference):
    """Get a technical field name given the template and date range references.

    :param template_reference: the technical reference of the field template
    :param range_reference: the technical reference of the date range
    :returns: the technical name of the field
    """
    return 'x__{template}__{range}'.format(
        template=template_reference, range=range_reference)
