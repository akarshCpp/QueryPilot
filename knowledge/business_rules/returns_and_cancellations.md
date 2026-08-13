# Business Rules

## Order Statuses
An order can be in one of three statuses:
1. **Pending**: The order is placed but payment or fulfillment is not complete. These should not be counted as sales or revenue.
2. **Completed**: The order has been fulfilled and paid for. These count towards revenue and sales volume.
3. **Cancelled**: The order was voided before completion. These do not count towards sales, revenue, or returns.

## Refunds and Returns
- Only sales from 'Completed' orders can be returned.
- A return indicates that the customer sent the item back.
- When calculating Net Revenue, the `refund_amount` from the `returns` table must be subtracted from the sales total.
- The reason for return (e.g., 'Defective', 'Changed mind') does not change the financial calculation, but is useful for product quality analytics.
