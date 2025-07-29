# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Karma User Dashboard',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://numigi.com/r/home',
    'license': 'LGPL-3',
    'category': 'Karma',
    'summary': 'Add a dashboard to display the user Karma scores.',
    'depends': [
        'karma',
    ],
    'data': [
        'views/assets.xml',
        'views/dashboard_menu_item.xml',
        'views/karma_display_on_dashboard.xml',
    ],
    'qweb': [
        'static/src/xml/dashboard.xml',
    ],
    'installable': True,
}
