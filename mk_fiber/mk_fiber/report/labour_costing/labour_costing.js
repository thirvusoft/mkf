// Copyright (c) 2016, mk and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Labour Costing"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"width": "80"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname":"employee_name",
			"label": __("Employee Name"),
			"fieldtype": "Link",
			"options": "Employee"
		}

	]
};

