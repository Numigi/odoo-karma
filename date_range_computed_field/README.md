# Date Range Computed Field

This module allows to define templates of computed fields.

Each template can be used to generate multiple computed fields on a model.
Each generate field is computed with a distinct date interval.

For example, you could define a field template for a partner's invoiced amount over a period of time.

| Label | Model | Technical Reference | Active |
|-|-|-|-|
| Invoiced Amount | Partner | customer_invoiced_amount | [ x ] |

Then you may combine the field template with date intervals:

| Field Template | Date Interval | Active |
|-|-|-|
| Partner - Invoiced Amount | Current Month | [ x ] |
| Partner - Invoiced Amount | Year-To-Date | [ x ] |
| Partner - Invoiced Amount | Previous Month | [ x ] |
| Partner - Invoiced Amount | Previous Year | [ x ] |
