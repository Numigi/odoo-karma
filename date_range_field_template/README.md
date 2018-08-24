# Date Range Field Template

This module allows to define templates of computed fields.

Each template can be used to generate multiple computed fields on a model.
Each generate field is computed with a distinct date range.

For example, you could define a field template for a partner's invoiced amount over a period of time.

| Label | Model | Technical Reference | Active |
|-------|-------|---------------------|--------|
| Invoiced Amount | Partner | customer_invoiced_amount | [ x ] |

Then you may combine the field template with date ranges:

| Field Template | Date Range | Active |
|----------------|------------|--------|
| Partner - Invoiced Amount | Current Month | [ x ] |
| Partner - Invoiced Amount | Year-To-Date | [ x ] |
| Partner - Invoiced Amount | Previous Month | [ x ] |
| Partner - Invoiced Amount | Previous Year | [ x ] |


## Defining a Field Template

In your custom module, you must define a function to compute the field.

```python
def compute_invoiced_amount(records, field_name, date_from, date_to):
    for partner in records:
        ...
        partner[field_name] = ...

```

Next, you must register the field template for your model (in this case, the model is res.partner).

```python

from odoo import models

class ResPartner(models.Model):

    _inherit = 'res.partner'

    def _register_hook(self):
        super()._register_hook()
        self._register_date_range_field('invoiced_amount', compute_invoiced_amount)
```

The last step is to define the field template in xml data.

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="invoiced_amount_template" model="computed.field.template">
        <field name="name">Invoiced Amount</field>
        <field name="reference">invoiced_amount</field>
        <field name="model_id" ref="base.model_res_partner"/>
        <field name="field_type">monetary</field>
    </record>

</odoo>
```

The bottom line is that the field you just defined is now reusable with any range type.

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
