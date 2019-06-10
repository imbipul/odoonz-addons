# -*- coding: utf-8 -*-
# Copyright 2019 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Anglosaxon Financial",
    "description": """
        Allows purely financial invoices and credits in anglosaxon environments""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Graeme Gellatly",
    "website": "https://o4sb.com",
    "depends": ["account", "stock_account", "purchase_stock", "sale_stock"],
    "data": ["wizards/account_invoice_refund.xml", "views/account_invoice.xml"],
    "demo": [],
}
