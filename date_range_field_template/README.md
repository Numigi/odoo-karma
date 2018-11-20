# Date Range Field Template

This module allows to define templates of computed fields.

Each template can be used to generate multiple computed fields on a model.
Each generate field is computed with a distinct date range.

For example, you could define a field template for a partner's invoiced amount over a period of time.

| Name | Model | Technical Reference |
|------|-------|---------------------|
| Invoiced Amount | Partner | customer_invoiced_amount |

Then you may combine the field template with date ranges:

| Date Range | Field |
|------------|----------------|
|Current Month | Invoiced Amount (Current Month) |
|Year-To-Date | Invoiced Amount (Year-To-Date) |
|Previous Month | Invoiced Amount (Previous Month) |
|Previous Year | Invoiced Amount (Previous Year) |


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

## Related Model

Field templates can accept an extra argument `related_model` which expects an `ir.model` record.

Here is an example for the number of messages sent by a user.

```python
def compute_number_messages_sent(records, field_name, date_from, date_to, related_model):
    for user in records:
        messages = user.env['mail.message'].search([
            ...
            ('model', '=', related_model.model),
        ], count=True)
        ...
        users[field_name] = ...

```

In the XML of the field template, `related_model_argument` must be enabled.

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="number_messages_sent_template" model="computed.field.template">
        <field name="name">Number Messages Sent</field>
        <field name="reference">number_messages_sent</field>
        <field name="model_id" ref="base.model_res_users"/>
        <field name="field_type">integer</field>
        <field name="related_model_argument" eval="True"/>
    </record>

</odoo>
```

Then, in the form view of the field template, an extra column will be added
to specify the model:

| Date Range | Related Model | Field |
|------------|---------------|-------|
|Current Month | Customer Invoice | Number Messages Sent (Customer Invoice / Current Month) |
|Current Month | CRM Lead | Invoiced Amount (CRM Lead / Current Month) |

Contributors
------------
* Numigi (tm) and all its contributors (https://bit.ly/numigiens)

More information
----------------
* Meet us at https://bit.ly/numigi-com
