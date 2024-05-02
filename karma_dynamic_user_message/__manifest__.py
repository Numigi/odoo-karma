# Copyright 2024 Numigi (tm) and all its contributors (https://bit.ly/numigiens)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Karma Dynamic User Message",
    "version": "1.0.0",
    "author": "Numigi",
    "maintainer": "Numigi",
    "website": "https://bit.ly/numigi-com",
    "license": "AGPL-3",
    "category": "Karma",
    "depends": [
        "karma",
    ],
    "summary": """
        Enrich the Karma operation in order to have a blocking message on one
        if the fields of a record, if the condition configured in the Karma
        model is true.
    """,
    "data": [
        "views/assets.xml",
        "views/karma.xml",
    ],
    "installable": True,
}
