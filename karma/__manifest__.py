# © 2018 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Karma',
    'version': '1.0.1',
    'author': 'Numigi',
    'maintainer': 'Numigi',
    'website': 'https://bit.ly/numigi-com',
    'license': 'LGPL-3',
    'category': 'Karma',
    'summary': 'Compute scores on all types of records.',
    'depends': [
        'decimal_precision',
        'date_range_field_template',
        'queue_job',
    ],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/karma_score.xml',
        'views/karma_score_detail.xml',
        'views/karma_error_log.xml',
        'views/karma_session.xml',
        'views/karma.xml',
        'views/menu.xml',
        'data/ir_cron.xml',
        'data/ir_sequence.xml',
    ],
    'qweb': [
        'static/src/xml/karma_widget.xml',
    ],
    'installable': True,
    'application': True,
}
