import frappe
from frappe import _
from erpnext.stock.doctype.batch.batch import get_batch_qty
from erpnext.stock.stock_ledger import get_previous_sle
from frappe.utils import nowdate, nowtime


def execute(filters={}):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data


def throw_error(item):
	frappe.throw(f"Value missing in TS Settings: {item}")


def get_data(filters):

	ts_item=frappe.get_single('TS Settings')
	
	co_kg=ts_item.coconut_in_kg or throw_error("Coconut in Kg")
	co_nos=ts_item.coconut_in_nos or throw_error("Coconut in Nos")
	ud_kg=ts_item.udaithengai_in_kg or throw_error("Udaithengai in Kg")
	ud_nos=ts_item.udaithengai_in_nos or throw_error("Udaithengai in Nos")
	ur_kg=ts_item.urithengai_in_kg or throw_error("Urithengai in Kg")
	ur_nos=ts_item.urithengai_in_nos or throw_error("Urithengai in Nos")
	husk=ts_item.husk or throw_error("Husk")
	shell=ts_item.shell or throw_error("Shell")
	copra=ts_item.copra or throw_error("Copra")
	
	item_list={'coco_nos':co_nos, 'coco_kg':co_kg, 'uri_nos':ur_nos, 'uri_kg':ur_kg, 'copra':copra, 'shell':shell, 'husk':husk, 'wages':'wages'}
	wh_wise_qty={}
	ts_batch_dict=frappe.get_all("Batch",filters, ['name', 'item', 'parent_batch_id'])
	if(filters.get('parent_batch_id')):
		bat=frappe.get_all("Batch",{'name': filters.get('parent_batch_id')}, ['name', 'item', 'parent_batch_id'])
		bat[0]['parent_batch_id']=filters['parent_batch_id']
		ts_batch_dict+=bat
	batch_dict = []
	for batch in ts_batch_dict:
		batch_qty=get_batch_qty(batch['name'])
		batch['batch_qty'] = sum([bat.get('qty') for bat in batch_qty])
		batch_dict.append(batch)
		for ts_bat in batch_qty:
			if(ts_bat['warehouse'] not in wh_wise_qty):
				wh_wise_qty[ts_bat['warehouse']]={}
			tsbat=frappe.get_value('Batch', batch['name'], 'parent_batch_id') or batch['name']
			if(tsbat not in wh_wise_qty[ts_bat['warehouse']]):
				wh_wise_qty[ts_bat['warehouse']][tsbat]={}
			if(batch['item'] not in wh_wise_qty[ts_bat['warehouse']][tsbat]):
				wh_wise_qty[ts_bat['warehouse']][tsbat][batch['item']]=0
			wh_wise_qty[ts_bat['warehouse']][tsbat][batch['item']]+=ts_bat['qty']
		
	batch_list=[bat['name'] for bat in batch_dict]
	
	sales_value, last_sales_rate = batch_sales_value(batch_list, item_list)
	stock_value = batch_stock_value(batch_dict, batch_list, last_sales_rate, item_list)
	purchase_value = batch_purchase_value(batch_list, item_list)
	wages_value = batch_wages_value(batch_list)
	
	data = final_data(wh_wise_qty, purchase_value, wages_value, stock_value, sales_value, item_list)
	return data
	
def batch_stock_value(batch_dict, batch_list, last_sales_rate, item_list):
	stock_value={}
	for bat in batch_dict:
		if(bat['item'] in [item_list['husk'], item_list['shell'], item_list['copra']]):
			if(bat['parent_batch_id'] not in stock_value):
				stock_value[bat['parent_batch_id']] = {
				item_list['husk']: {'qty':0, 'amount':0}, 
				item_list['shell']: {'qty':0, 'amount':0}, 
				item_list['copra']: {'qty':0, 'amount':0}}
			stock_value[bat['parent_batch_id']][bat['item']]['qty'] += bat['batch_qty']
			stock_value[bat['parent_batch_id']][bat['item']]['amount'] += bat['batch_qty']*last_sales_rate[bat['item']]
	return stock_value
	
	
def batch_sales_value(batch_list, item_list):
	ts_settings = frappe.get_single('TS Settings')
	if(ts_settings.change_market_value_in_report):
		husk = ts_settings.husk_market_rate or 0
		shell = ts_settings.shell_market_rate or 0
		copra = ts_settings.copra_market_rate or 0
	else:
		try:
			husk=(frappe.get_last_doc('Sales Invoice Item', {'item_code':item_list['husk'], 'docstatus':1})).rate
		except frappe.DoesNotExistError as e:
			husk=0	
		try:
			shell=(frappe.get_last_doc('Sales Invoice Item', {'item_code':item_list['shell'], 'docstatus':1})).rate
		except frappe.DoesNotExistError as e:
			shell=0
		try:	
			copra=(frappe.get_last_doc('Sales Invoice Item', {'item_code':item_list['copra'], 'docstatus':1})).rate
		except frappe.DoesNotExistError as e:
			copra=0
	
	last_sales_rate={item_list['husk']: husk, item_list['shell']: shell, item_list['copra']: copra}
	
	sales_value = {}
	sii = frappe.get_all("Sales Invoice Item", {'batch_no':['in', batch_list],  'item_code':['in', [item_list['husk'], item_list['shell'], item_list['copra']]], 'docstatus':1}, ['item_code', 'batch_no', 'qty', 'amount'])
	for doc in sii:
		batch = frappe.get_value('Batch', doc['batch_no'], 'parent_batch_id') or doc['batch_no']
		if(batch not in sales_value):
			sales_value[batch] = {
			item_list['husk']: {'qty':0, 'amount':0}, 
			item_list['shell']: {'qty':0, 'amount':0}, 
			item_list['copra']: {'qty':0, 'amount':0}}
			
		sales_value[batch][doc['item_code']]['qty']+=doc['qty']
		sales_value[batch][doc['item_code']]['amount']+=doc['amount']
	return sales_value, last_sales_rate

	
def batch_purchase_value(batch_list, item_list):
	purchase_value = {}
	pri= frappe.get_all('Purchase Receipt Item', {'batch_no':['in', batch_list], 'docstatus':1}, ['batch_no', 'qty', 'amount'])
	for doc in pri:
		batch = frappe.get_value('Batch', doc['batch_no'], 'parent_batch_id') or doc['batch_no']
		if(batch not in purchase_value):
			purchase_value[batch] = {'qty':0, 'amount':0}
		purchase_value[batch]['qty']+=doc['qty']
		purchase_value[batch]['amount']+=doc['amount']
	return purchase_value


def batch_wages_value(batch_list):
	wages_value = {}
	sei= frappe.get_all('Stock Entry Detail', {'docstatus': 1, 'ts_additional_cost':['!=', 0], 's_warehouse': '', 't_warehouse': ['!=', '']}, ['ts_additional_cost', 'batch_no'])
	pri= frappe.get_all('Purchase Receipt Item', {'docstatus': 1, 'ts_additional_cost':['!=', 0]}, ['ts_additional_cost', 'batch_no'])
	sii= frappe.get_all('Sales Invoice Item', {'docstatus': 1, 'ts_additional_cost':['!=', 0]}, ['ts_additional_cost', 'batch_no'])

	# dni= frappe.get_all('Delivery Note Item', {'docstatus': 1, 'ts_additional_cost':['!=', 0]}, ['ts_additional_cost', 'batch_no'])
	for details in sei+pri+sii:
		batch = frappe.get_value('Batch', details['batch_no'], 'parent_batch_id') or details['batch_no']
		if(batch not in wages_value):
			wages_value[batch]=0
		wages_value[batch]+=details['ts_additional_cost']
			
	return wages_value


def get_valuation_rate(item_code):
	rate={}
	for warehouse in frappe.get_all('Warehouse',pluck='name'):
		args = {
			"item_code": item_code,
			"warehouse": warehouse,
			"posting_date": nowdate(),
			"posting_time": nowtime(),
		}
		last_entry = get_previous_sle(args)
		rate[warehouse]=last_entry.valuation_rate if last_entry else 0.0
	return rate


def final_data(wh_wise_qty, purchase_value, wages_value, stock_value, sales_value, item_list):
	parent_batch_list = frappe.get_all('Batch', {'parent_batch_id': ''}, pluck='name')
	data=[]
	husk_wh_rate=get_valuation_rate(item_list['husk'])
	shell_wh_rate=get_valuation_rate(item_list['shell'])
	copra_wh_rate=get_valuation_rate(item_list['copra'])
	for batch in parent_batch_list:
		tsbat=frappe.get_value('Batch', batch, 'parent_batch_id') or batch
		data_dict={
			'batch': batch,
			'husk_qty': ((stock_value.get(batch) or {}).get(item_list['husk']) or {}).get('qty') or 0,
			'shell_qty': ((stock_value.get(batch) or {}).get(item_list['shell']) or {}).get('qty') or 0,
			'copra_qty': ((stock_value.get(batch) or {}).get(item_list['copra']) or {}).get('qty') or 0,
			'husk_stock': sum([husk_wh_rate[wh]*(((wh_wise_qty.get(wh) or {}).get(tsbat) or {}).get(item_list['husk']) or 0) for wh in husk_wh_rate]),
			'shell_stock': sum([shell_wh_rate[wh]*(((wh_wise_qty.get(wh) or {}).get(tsbat) or {}).get(item_list['shell']) or 0) for wh in shell_wh_rate]),
			'copra_stock': sum([copra_wh_rate[wh]*(((wh_wise_qty.get(wh) or {}).get(tsbat) or {}).get(item_list['copra']) or 0) for wh in copra_wh_rate]),
			'husk_market': ((stock_value.get(batch) or {}).get(item_list['husk']) or {}).get('amount') or 0,
			'shell_market': ((stock_value.get(batch) or {}).get(item_list['shell']) or {}).get('amount') or 0,
			'copra_market': ((stock_value.get(batch) or {}).get(item_list['copra']) or {}).get('amount') or 0,
		}
		data_dict['stock_value']=data_dict['copra_stock']+data_dict['husk_stock']+data_dict['shell_stock']
		data_dict['market_value']=data_dict['copra_market']+data_dict['husk_market']+data_dict['shell_market']
		data.append(data_dict)
	return data


def get_columns(filters):
	columns=[
		{
			"label": _("Lot No"),
			"fieldname": "batch",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Husk Qty"),
			"fieldname": "husk_qty",
			"fieldtype": "Float",
			"precision":2,
			"width": 150
		},
		{
			"label": _("Husk Stock Value"),
			"fieldname": "husk_stock",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Husk Market Value"),
			"fieldname": "husk_market",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Shell Qty"),
			"fieldname": "shell_qty",
			"fieldtype": "Float",
			"precision":2,
			"width": 150
		},
		{
			"label": _("Shell Stock Value"),
			"fieldname": "shell_stock",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Shell Market Value"),
			"fieldname": "shell_market",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Copra Qty"),
			"fieldname": "copra_qty",
			"fieldtype": "Float",
			"precision":2,
			"width": 150
		},
		{
			"label": _("Copra Stock Value"),
			"fieldname": "copra_stock",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Copra Market Value"),
			"fieldname": "copra_market",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Total Stock Value"),
			"fieldname": "stock_value",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Total Market Value"),
			"fieldname": "market_value",
			"fieldtype": "Currency",
			"width": 150
		}
	]
	return columns