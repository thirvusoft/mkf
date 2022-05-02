# Copyright (c) 2022, mk and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from webbrowser import get
from frappe import _
import frappe

def execute(filters=None):
	data = get(filters)
	columns = get_columns(filters)
	return columns, data

def get(filters):
		purchase_rec = frappe.get_all("Purchase Receipt",pluck = 'name')
		batch_lis = frappe.get_all("Batch",pluck='name')
		for pr in purchase_rec:
			pr_doc = frappe.get_doc("Purchase Receipt",pr)
			for bat in pr_doc.items:
				bat_in_pr = bat.batch_no
				for i in batch_lis:
					bat_doc = frappe.get_doc("Batch",i)
					if bat_in_pr == bat_doc.name:
						for lis in bat_doc.ts_costing_details:
							x = []
							x = lis.doc_name
						frappe.errprint(x)	#for checking

def get_columns(filters):
	columns = [
		_("Supplier")+":Data:100",
		_("Item Code")+":Data:100",
		_("Batch No")+":Data:100",
		_("Total Qty")+":Data:100",
		_("Total Thengai Qty In Nos")+":Data:100",
		_("Total Thengai Qty In Kgs")+":Data:100",
		_("Total Urithangai Qty In Nos")+":Data:100",
		_("Total Urithangai Qty In Kgs")+":Data:100",
		_("Total Paruppu In Kgs")+":Data:100",
		_("Total Paruppu Percentage")+":Data:100",
		_("Total Shell Qty")+":Data:100",
		_("Total Husk Qty")+":Data:100",
		_("Total Sales Amount")+":Data:100",
		_("Total Profit Amount")+":Data:100",
		_("Wages")+":Data:100",
	]
	return columns