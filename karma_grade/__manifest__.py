# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Karma Grade',
    'version': '1.0.1',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://numigi.com/r/home',
    'license': 'LGPL-3',
    'category': 'Karma',
    'depends': ['karma'],
    'data': [
        'views/karma_with_grades.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/karma_widget_with_grades.xml',
    ],
    'installable': True,
}
