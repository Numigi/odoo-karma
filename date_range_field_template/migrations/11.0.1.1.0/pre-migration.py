# © Numigi (tm) and all its contributors (https://numigi.com/r/home)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openupgradelib.openupgrade import logged_query


def migrate(cr, version):
    """Delete the `unique_reference` constraint on field templates."""
    logged_query(cr, """
        ALTER TABLE computed_field
        DROP CONSTRAINT IF EXISTS computed_field_unique_reference;
    """)
