from asyncio import constants
import frappe
from frappe import _


def execute(filters=None):
	print(filters)
	columns, data = [] , []
	columns = get_columns()
	repack_items = frappe.get_list('Stock Entry Detail', {'item_code', 'item_name', 'qty', 'batch_no', 'parent'})

	print(repack_items)
	print(frappe.get_list('Stock Entry Detail', {'item_code', 'item_name', 'qty', 'batch_no', 'parent'}))
	pr_items = frappe.get_list('Purchase Receipt Item', {'item_code', 'item_name', 'qty', 'batch_no', 'parent'})
	final_data = []
	for row in pr_items:
		purchase_item_wise_se_list = frappe.get_list('Stock Entry Detail', {'item_code':row['item_code'], 'batch_no':row['batch_no']},['parent'])
		total_paruppu_qty = 0
		for row1 in purchase_item_wise_se_list:
			total_paruppu_qty += sum(frappe.get_list('Stock Entry Detail', {'item_code':'T4'}, ['qty'],pluck='qty'))
		final_data.append({'supplier':frappe.db.get_value('Purchase Receipt', row['parent'], 'supplier'), 
							'item_code':row['item_code'],
							'item_name':row['item_name'],
							'batch_no':row['batch_no'],
							'total_qty':row['qty'],
							'total_paruppu_qty': total_paruppu_qty,
							'profit_percentage':(total_paruppu_qty/row['qty'])*100 if total_paruppu_qty else 0})

	# supplier = filters.get("customer")
	# conditions = ""
	# if supplier:
	# 		conditions += " and sup.name = '{0}' ".format(supplier)

	# report_data = frappe.db.sql("""
	# 							select pr.supplier,pri.item_code,sed.batch_no
	# 							from `tabPurchase Receipt Item` as pri
	# 									left outer join `tabItem` as item on 
	# 										item.item_code = pri.item_code 
	# 									left outer join `tabPurchase Receipt` as pr 
	# 										on pr.name = pri.parent 
	# 									left outer join `tabStock Entry Detail` as sed on 
	# 										sed.batch_no = pri.batch_no
										
	# 							group by pri.item_code;
								
	# 			""".format(conditions))

	# columns, data = get_columns(), report_data
	return columns, final_data


def get_columns():
	columns = [
		_("Supplier") + ":Link/Supplier:150",
		_("Item Code") + ":Link/Item:200",
		_("Batch No") + "::150",
		_("Total Qty") + "::100",
		_("Total Paruppu Qty") + "::100",
		_("Profit Percentage") + "::100"
	]
	return columns

