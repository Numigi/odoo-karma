# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Karma CRM',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://numigi.com/r/home',
    'license': 'LGPL-3',
    'category': 'Karma',
    'summary': 'Add the karma widget on the crm leads and teams form view.',
    'depends': ['karma', 'sale_crm', 'sales_team'],
    'data': [
        'views/crm_view.xml',
    ],
    'installable': True,
}
