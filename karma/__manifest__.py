# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Karma',
    'version': '1.0.0',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Other',
    'summary': 'Compute scores on all types of records.',
    'depends': [
        'decimal_precision',
        'queue_job',
    ],
    'data': [
        'views/assets.xml',
        'views/karma_score.xml',
        'views/karma_score_detail.xml',
        'views/karma.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
