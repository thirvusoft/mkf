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
	if(filters == None):
		pass
	else:
		pur_rec_list = frappe.get_all("GL Entry",pluck='name')
		for i in pur_rec_list:
			doc = frappe.get_doc("GL Entry",i)
			frappe.errprint(doc)
		# frappe.errprint(pur_rec_list)

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