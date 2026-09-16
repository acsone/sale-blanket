# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.constrains("order_type", "price_unit", "is_delivery")
    def _check_call_off_order_line_price(self):
        # exludes delivery lines from the check, as they are not linked to a blanket
        # order line and their price is computed on the call-off order itself.
        to_check = self.filtered(
            lambda line: not line.is_delivery and line.order_type == "call_off"
        )
        return super(SaleOrderLine, to_check)._check_call_off_order_line_price()

    def _get_manual_delivery_procurement_group_domain(self):
        domain = super()._get_manual_delivery_procurement_group_domain()
        manual_delivery = self.env.context.get("sale_manual_delivery")
        call_off_order = self._get_call_off_order_to_deliver()
        if manual_delivery and call_off_order:
            domain.append(("carrier_id", "=", call_off_order.carrier_id.id))
        return domain

    def _prepare_procurement_group_vals(self):
        vals = super()._prepare_procurement_group_vals()
        call_off_order = self._get_call_off_order_to_deliver()
        if call_off_order:
            # Overrides the carrier_id set by delivery_procurement_group_carrier
            # (which reads it from self.order_id, i.e. the blanket order): the
            # call-off order may use a different delivery method than the one
            # defined on the blanket order.
            vals["carrier_id"] = call_off_order.carrier_id.id
        return vals
