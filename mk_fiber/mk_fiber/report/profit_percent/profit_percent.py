from asyncio import constants
import frappe
from frappe import _


def execute(filters=None):
	supplier = filters.get("customer")
	conditions = ""
	if supplier:
			conditions += " and sup.name = '{0}' ".format(supplier)
	frappe.errprint(conditions)

	report_data = frappe.db.sql("""
								select pr.supplier,pri.item_code,sed.batch_no
								from `tabPurchase Receipt Item` as pri
										left outer join `tabItem` as item on 
											item.item_code = pri.item_code
										left outer join `tabPurchase Receipt` as pr 
											on pr.name = pri.parent 
										left outer join `tabStock Entry Detail` as sed on 
											sed.batch_no = pri.batch_no
										
								group by pri.item_code;
								
				""".format(conditions))

	frappe.errprint(report_data)
	columns, data = get_columns(), report_data
	return columns, data


def get_columns():
	columns = [
		_("Supplier") + ":Link/Supplier:150",
		_("Item Code") + ":Link/Item:100",
		_("Batch No") + "::100"
	]
	return columns