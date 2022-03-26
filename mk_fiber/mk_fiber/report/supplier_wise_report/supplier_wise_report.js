// Copyright (c) 2022, mk and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supplier Wise Report"] = {
	"filters": [
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier"
		},
		{
			"fieldname":"start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.month_start(),
			"reqd":1
		},
		{
			"fieldname":"end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.month_end(),
			"reqd":1
		}
	]
};
