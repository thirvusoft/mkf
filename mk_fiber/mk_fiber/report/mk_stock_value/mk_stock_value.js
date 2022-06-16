frappe.query_reports["MK Stock Value"] = {
	"filters": [
		{
			"fieldname":"parent_batch_id",
            "label": __("Lot"),
            "fieldtype": "Link",
            "options": "Batch",
            "filters":{'parent_batch_id':''},
		}
	],
	
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname=='husk_qty' || column.fieldname=='husk_stock' || column.fieldname=='husk_market') {
			value = "<div style='background-color:#FAFAD2;font-weight:bold;'>"+value+"</div>"
		}
		if (column.fieldname=='shell_qty' || column.fieldname=='shell_stock' || column.fieldname=='shell_market') {
			value = "<div style='background-color:#D2B48C;font-weight:bold;'>"+value+"</div>"
		}
		if (column.fieldname=='copra_qty' || column.fieldname=='copra_stock' || column.fieldname=='copra_market') {
			value = "<div style='background-color:#FAFAD2;font-weight:bold;'>"+value+"</div>"
		}
		return value;
	}
};
