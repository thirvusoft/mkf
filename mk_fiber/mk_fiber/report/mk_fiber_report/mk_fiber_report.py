# Copyright (c) 2022, mk and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from time import clock_getres
from webbrowser import get
from frappe import _
import frappe
from frappe.utils.jinja import set_filters

def execute(filters=None):
	data = get(filters)
	columns = get_columns(filters)
	return columns, data

def throw_error(item):
	frappe.throw(f"Value missing in TS Item Settings: {item}")

def get(filters):
	pr_filters={}
	pr_filters['docstatus']=1
	
	se_filters={}
	se_filters['docstatus']=1
	se_filters['stock_entry_type']='Repack'
	
	
	ts_item=frappe.get_single('TS Item Settings')
	
	co_kg=ts_item.coconut_in_kg or throw_error("Coconut in Kg")
	co_nos=ts_item.coconut_in_nos or throw_error("Coconut in Nos")
	ud_kg=ts_item.udaithengai_in_kg or throw_error("Udaithengai in Kg")
	ud_nos=ts_item.udaithengai_in_nos or throw_error("Udaithengai in Nos")
	ur_kg=ts_item.urithengai_in_kg or throw_error("Urithengai in Kg")
	ur_nos=ts_item.urithengai_in_nos or throw_error("Urithengai in Nos")
	husk=ts_item.husk or throw_error("Husk")
	shell=ts_item.shell or throw_error("Shell")
	copra=ts_item.copra or throw_error("Copra")
	
	pr=frappe.get_all('Purchase Receipt', filters=pr_filters, pluck='name')
	se=frappe.get_all('Stock Entry', filters=se_filters, pluck='name')
	
	batch_qty={}
	batch_supplier_qty={}
	batch_pr_rate={}
	batch_stock_entry={}
	batch_labour_cost={}
	
	for doc in pr: 
		pr_doc=frappe.get_doc('Purchase Receipt', doc)
		for row in pr_doc.items:
			if(row.batch_no):
				if(row.batch_no not in batch_qty):
					batch_qty[row.batch_no]=0
				batch_qty[row.batch_no]+=row.qty
				if(row.batch_no not in batch_supplier_qty):
					batch_supplier_qty[row.batch_no]=[]
				batch_supplier_qty[row.batch_no].append([pr_doc.supplier, row.item_code, row.qty])
				if(row.batch_no not in batch_pr_rate):
					batch_pr_rate[row.batch_no]=0
				batch_pr_rate[row.batch_no]+=row.amount
				
	frappe.errprint(batch_qty)
	frappe.errprint(batch_supplier_qty)
	frappe.errprint(batch_pr_rate)

	
	for doc in se:
		se_doc=frappe.get_doc('Stock Entry',doc)
		run=True
		for row in se_doc.items:
			batch=row.batch_no
			if(not batch):
				continue
			ts_batch=frappe.db.get_value('Batch', batch, 'parent_batch_id')
			if(ts_batch):
				batch=ts_batch
			if(batch not in batch_stock_entry):
				batch_stock_entry[batch]={co_kg:0,
										co_nos:0,
										ur_kg:0,
										ur_nos:0,
										ud_kg:0,
										ud_nos:0,
										copra:0,
										husk:0,
										shell:0,
										'wages':0
										}
			if(row.t_warehouse):				
				if(row.item_code in batch_stock_entry[batch]):
					batch_stock_entry[batch][row.item_code]+=row.qty
					
			if(row.s_warehouse and run):
				run=False
				total_cost=0
				for lab in se_doc.labour_details:
					total_cost+=(lab.total_cost or 0)
				batch_stock_entry[batch]['wages']+=total_cost
		
	# frappe.errprint(batch_stock_entry)
	
	batch_supplier_ratio=supplier_ratio(batch_qty, batch_supplier_qty)




def supplier_ratio(batch_qty, batch_supplier_qty):
	batch_supplier_ratio={}
	for bat in batch_supplier_qty:
		if(bat not in batch_supplier_ratio):
			batch_supplier_ratio[bat]=[]
		for sup in batch_supplier_qty[bat]:
			add=True
			for bat_sup in batch_supplier_ratio:
				if(sup[0] in bat_sup):
					add=False
			if(add):
				batch_supplier_ratio[bat].append({sup[0]:0})
			for bat_sup in batch_supplier_ratio[bat]:
				idx=batch_supplier_ratio[bat].index(bat_sup)
				if(sup[0] in bat_sup):
					batch_supplier_ratio[bat][idx][sup[0]]+=(sup[2])
		
		for bat_sup in batch_supplier_ratio[bat]:
			idx=batch_supplier_ratio[bat].index(bat_sup)
			if(sup[0] in bat_sup):
				# frappe.errprint(batch_supplier_ratio[bat][idx][sup[0]])
				batch_supplier_ratio[bat][idx][sup[0]]/=batch_qty[bat]
				batch_supplier_ratio[bat][idx][sup[0]]*=100
	# 			frappe.errprint(batch_supplier_ratio[bat][idx][sup[0]])
	# 			frappe.errprint('\n')
	
	# frappe.errprint(batch_supplier_ratio)
	




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
		_("Total Purchase Amount")+":Currency:100",
		_("Total Sales Amount")+":Currency:100",
		_("Total Profit Amount")+":Currency:100",
		_("Wages")+":Currency:100",
	]
	return columns