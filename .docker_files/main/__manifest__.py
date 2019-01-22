# © 2018 Numigi
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Main Module',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://www.numigi.com',
    'license': 'LGPL-3',
    'category': 'Other',
    'summary': 'Install all addons required for testing.',
    'depends': [
        # Modules used to test karma addons
        'gamification',
        'sale',
        'stock',

        'date_range_field_template',
        'form_view_image_120px',
        'karma',
        'karma_crm',
        'karma_grade',
        'karma_partner',
        'karma_product',
        'karma_project',
        'karma_required_field',
        'karma_user_dashboard',
    ],
    'installable': True,
}
