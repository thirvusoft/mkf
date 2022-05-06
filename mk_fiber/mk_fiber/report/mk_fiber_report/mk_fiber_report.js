// Copyright (c) 2022, mk and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["MK Fiber Report"] = {
	"filters": [
		{
			"fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
			"default":frappe.datetime.month_start()
		},
		{
			"fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
			"default":frappe.datetime.month_end()
		},
		{
			"fieldname":"supplier",
            "label": __("Supplier"),
            "fieldtype": "Link",
            "options": "Supplier"
		},
		{
			"fieldname":"purchase_receipt_no",
            "label": __("Purchase Receipt No"),
            "fieldtype": "Link",
            "options": "Purchase Receipt"
		},
	]
};
