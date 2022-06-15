frappe.query_reports["MK Stock Value"] = {
	"filters": [
		{
			"fieldname":"parent_batch_id",
            "label": __("Lot"),
            "fieldtype": "Link",
            "options": "Batch",
            "filters":{'parent_batch_id':''},
		}
	]
};
