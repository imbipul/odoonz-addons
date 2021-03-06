# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    """inherits account.account_invoice and adds the order_partner_id field
    as well as overriding ORM functions to ensure the parent partner and order
    partner are written and created correctly"""
    _inherit = "account.invoice"

    order_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Commercial Partner"
    )

    order_invoice_id = fields.Many2one(
        comodel_name="res.partner", string="Invoice Partner"
    )

    @api.multi
    def _get_invoice_partner(self):
        """
        Hook method for extensibility to determine which partner should be used
        for checking the lock date
        :return: A res.partner recordset
        """
        return super()._get_invoice_partner() + self.order_partner_id

    @api.constrains("partner_id", "order_partner_id")
    def check_company(self):
        for record in self:
            if record.company_id.partner_id.id in [
                record.partner_id.id,
                record.partner_id.commercial_partner_id.id,
            ]:
                raise ValidationError(_("Cannot self bill"))

    @api.model_create_multi
    def create(self, vals_list):
        """Function overrides create to ensure that parent account is
        always used"""
        Partner = self.env["res.partner"]
        for vals in vals_list:
            if vals.get("partner_id"):
                order_partner = Partner.browse(vals["partner_id"])
                partner = order_partner.commercial_partner_id
                invoice_partner = partner.get_billing_partner(vals)
                if invoice_partner != partner:
                    vals.update(
                        {
                            "partner_id": invoice_partner.id,
                            "order_partner_id": partner.id,
                            "order_invoice_id": order_partner.id,
                        }
                    )
        return super().create(vals_list)

    @api.multi
    def write(self, vals):
        """Function overrides create to ensure that parent account is
        always used"""
        if vals.get("partner_id", False):
            Partner = self.env["res.partner"]
            partner = Partner.browse(vals["partner_id"]).commercial_partner_id
            invoice_partner = partner.get_billing_partner(vals, self[0])
            if invoice_partner != partner:
                vals.update(
                    {
                        "partner_id": invoice_partner.id,
                        "order_partner_id": partner.id,
                        "order_invoice_id": vals["partner_id"],
                    }
                )
        return super().write(vals)

    @api.model
    def _search(self, args, **kwargs):
        """override search so we find subsidiary invoices when looking at
        that partner.
       """
        iter_args = list(args)
        args = []
        for arg in iter_args:
            if arg[0] == "partner_id" and arg[1] in (
                "=",
                "like",
                "ilike",
                "child_of",
            ):
                args.extend(["|", arg, ("order_partner_id", arg[1], arg[2])])
            else:
                args.append(arg)
        return super()._search(args, **kwargs)

    def _get_refund_common_fields(self):
        return super()._get_refund_common_fields() + [
            "order_partner_id",
            "order_invoice_id",
        ]
