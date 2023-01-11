# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Date Range Field Template',
    'version': '1.1.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Karma',
    'summary': 'Enable generating computed fields from templates based on date ranges.',
    'depends': ['base', 'stock', 'gamification'],
    'data': [
        'data/date_range.xml',
        'views/date_range.xml',
        'views/field_template.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
