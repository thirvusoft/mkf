import frappe
from frappe import _
import copy
from erpnext.stock.stock_ledger import get_previous_sle
from frappe.utils import nowdate, nowtime
from erpnext.stock.doctype.batch.batch import get_batch_qty


def execute(filters=None):
	data = get(filters)
	columns = get_columns(filters)
	return columns, data

def throw_error(item):
	frappe.throw(f"Value missing in TS Settings: {item}")

def get(filters):
	pr_filters={}
	pr_filters['docstatus']=1
	
	se_filters={}
	se_filters['docstatus']=1
	se_filters['stock_entry_type']='Repack'
	
	si_filters={}
	si_filters['docstatus']=1
	si_filters['update_stock']=1
	
	dn_filters={}
	dn_filters['docstatus']=1
	
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
	
	pr=frappe.get_all('Purchase Receipt', filters=pr_filters, pluck='name')
	se=frappe.get_all('Stock Entry', filters=se_filters, pluck='name')
	si=frappe.get_all('Sales Invoice', filters=si_filters, pluck='name')
	dn=frappe.get_all('Delivery Note', filters=dn_filters, pluck='name')

	pi_filters={}
	pi_filters['docstatus']=1
	pi_filters['purchase_receipt']=['in',pr]
	
	pi=frappe.get_all('Purchase Invoice Item', filters=pi_filters, pluck='name')

	item_dict={co_kg:0,
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
	item_list={'coco_nos':co_nos, 'coco_kg':co_kg, 'uri_nos':ur_nos, 'uri_kg':ur_kg, 'copra':copra, 'shell':shell, 'husk':husk, 'wages':'wages'}
	
	batch_qty={}
	batch_supplier_qty={}
	batch_pr_rate={}
	batch_si_rate={}
	batch_stock_entry={}
	batch_labour_cost={}
	batch_stock_qty={}
	
	batch_list=frappe.get_all('Batch', ['name', 'item', 'parent_batch_id'])
	for bat in batch_list:
		if(bat['item'] in [item_list['husk'], item_list['shell'], item_list['copra']]):
			if(bat['parent_batch_id'] not in batch_stock_qty):
				batch_stock_qty[bat['parent_batch_id']]=0
			ts_wh_qty=get_batch_qty(bat['name'])
			ts_wh_rate=get_valuation_rate(bat['item'])
			for ts_wh in ts_wh_qty:
				batch_stock_qty[bat['parent_batch_id']]+=ts_wh['qty']*(ts_wh_rate.get(ts_wh['warehouse']) or 0)
	
	for doc in pr: 
		pr_doc=frappe.get_doc('Purchase Receipt', doc)
		pr_qty={}
		additional_cost=pr_doc.ts_total_amount
		for row in pr_doc.items:
			if(filters.get('batch_no')):
				if(row.batch_no!=filters.get('batch_no')):
					continue
			if(row.batch_no):
				if(row.batch_no not in batch_qty):
					batch_qty[row.batch_no]=0
				batch_qty[row.batch_no]+=row.qty
				if(row.batch_no not in batch_supplier_qty):
					batch_supplier_qty[row.batch_no]={}
				if(pr_doc.supplier not in batch_supplier_qty[row.batch_no]):
					batch_supplier_qty[row.batch_no][pr_doc.supplier]=[0, pr_doc.name]
				batch_supplier_qty[row.batch_no][pr_doc.supplier][0]+= row.qty

				if(row.batch_no not in pr_qty):
					pr_qty[row.batch_no]=0
				pr_qty[row.batch_no]+=row.qty
		for batch in pr_qty:
			if(batch not in batch_labour_cost):
				batch_labour_cost[batch]={}
			if('wages' not in batch_labour_cost[batch]):
				batch_labour_cost[batch]['wages']=0
			batch_labour_cost[batch]['wages']+=additional_cost * (pr_qty[batch]/pr_doc.total_qty)


	for row in pi:
		pr_doc=frappe.get_doc('Purchase Receipt', frappe.get_value('Purchase Invoice Item',row,'purchase_receipt'))
		if(pr_doc.docstatus==1):
			row=frappe.get_doc('Purchase Invoice Item',row)
			if(row.ts_batch not in batch_pr_rate):
				batch=row.ts_batch
				if(not batch):
					continue
				ts_batch=frappe.db.get_value('Batch', batch, 'parent_batch_id')
				if(ts_batch):
					batch=ts_batch
				batch_pr_rate[batch]=0
			batch_pr_rate[row.ts_batch]+=row.amount

	for doc in si:
		si_doc=frappe.get_doc('Sales Invoice', doc)
		for row in si_doc.items:
			if(row.item_code in [item_list['husk'], item_list['shell'], item_list['copra']]):
				if(row.batch_no not in batch_si_rate):
					batch=row.batch_no
					if(not batch):
						continue
					ts_batch=frappe.db.get_value('Batch', batch, 'parent_batch_id')
					if(ts_batch):
						batch=ts_batch
					if(batch not in batch_si_rate):
						batch_si_rate[batch]=0
					batch_si_rate[batch]+=row.amount
	
	for doc in dn:
		dn_doc=frappe.get_doc('Delivery Note', doc)
		for row in dn_doc.items:
			if(row.item_code in [item_list['husk'], item_list['shell'], item_list['copra']]):
				if(row.batch_no not in batch_si_rate):
					batch=row.batch_no
					if(not batch):
						continue
					ts_batch=frappe.db.get_value('Batch', batch, 'parent_batch_id')
					if(ts_batch):
						batch=ts_batch
					if(batch not in batch_si_rate):
						batch_si_rate[batch]=0
					batch_si_rate[batch]+=row.amount
	
	
	
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
				batch_stock_entry[batch]=copy.deepcopy(item_dict)
			if(row.t_warehouse):				
				if(row.item_code in batch_stock_entry[batch]):
					batch_stock_entry[batch][row.item_code]+=row.qty
					
			if(row.s_warehouse and run):
				run=False
				total_cost=se_doc.ts_total_amount
				
				if(batch not in batch_labour_cost):
					batch_labour_cost[batch]={}
				if('wages' not in batch_labour_cost[batch]):
					batch_labour_cost[batch]['wages']=0
				batch_labour_cost[batch]['wages']+=total_cost
	
	batch_supplier_ratio=supplier_ratio(batch_qty, batch_supplier_qty)
	final_dict=batch_final_dict(filters, batch_stock_qty, batch_qty, batch_supplier_ratio, batch_supplier_qty, batch_stock_entry, batch_si_rate, batch_pr_rate, batch_labour_cost, item_list)
	return final_dict
	
	


def batch_final_dict(filters, batch_stock_qty, batch_qty, batch_supplier_ratio, batch_supplier_qty, batch_stock_entry, batch_si_rate, batch_pr_rate, batch_labour_cost, item_list):
	final_dict=[]
	pr_filters={}
	if(filters.get('from_date') and filters.get('to_date')):
		pr_filters['posting_date']=['between', (filters['from_date'], filters['to_date'])]
	if(filters.get('supplier')):
		pr_filters['supplier']=filters['supplier']
	if(filters.get('purchase_receipt_no')):
		pr_filters['name']=filters['purchase_receipt_no']
	
	pr=frappe.get_all('Purchase Receipt', filters=pr_filters, pluck='name')
	
	for bat in batch_supplier_qty:
		for sup in batch_supplier_qty[bat]:
			if(batch_supplier_qty[bat][sup][1] not in pr):
				continue
			res={}
			res['supplier']=sup
			item_code = frappe.get_value('Batch', bat, 'item')
			res['item_name']=frappe.get_value('Item', item_code, 'item_name')
			res['batch']=bat
			
			res['qty']=batch_supplier_qty[bat][sup][0]
			res['uri_kg']="%.2f"%(((batch_stock_entry.get(bat) or {}).get(item_list['uri_kg']) or 0)*batch_supplier_ratio[bat][sup]/100)
			res['uri_nos']="%.2f"%(((batch_stock_entry.get(bat) or {}).get(item_list['uri_nos']) or 0)*batch_supplier_ratio[bat][sup]/100)
			
			copra_qty=((batch_stock_entry.get(bat) or {}).get(item_list['copra']) or 0)*batch_supplier_ratio[bat][sup]/100
			
			res['copra']="%.2f"%(copra_qty)
			res['copra_percent']=round((copra_qty/batch_qty[bat])*100 ,2)
			res['shell']="%.2f"%(((batch_stock_entry.get(bat) or {}).get(item_list['shell']) or 0)*batch_supplier_ratio[bat][sup]/100)
			res['husk']="%.2f"%(((batch_stock_entry.get(bat) or {}).get(item_list['husk']) or 0)*batch_supplier_ratio[bat][sup]/100)
			
			purchase_amt=(batch_pr_rate.get(bat) or 0)*batch_supplier_ratio[bat][sup]/100
			sales_amt=(batch_si_rate.get(bat) or 0)*batch_supplier_ratio[bat][sup]/100
			stock_in_hand=(batch_stock_qty.get(bat) or 0)*batch_supplier_ratio[bat][sup]/100
			wages=(((batch_labour_cost.get(bat) or {}).get(item_list['wages']) or 0)*batch_supplier_ratio[bat][sup]/100)
			
			res['sales_amt']="%.2f"%sales_amt
			res['stock_in_hand']="%.2f"%(stock_in_hand)
			res['purchase_amt']="%.2f"%purchase_amt
			res['wages']="%.2f"%(((batch_labour_cost.get(bat) or {}).get(item_list['wages']) or 0)*batch_supplier_ratio[bat][sup]/100)
			
			res['profit']="%.2f"%((sales_amt+stock_in_hand)-(purchase_amt+wages))
			
			final_dict.append(res)
	final_dict.sort(key= lambda x: x['batch'])
	final_dict_1 = []
	if(len(final_dict)):
		keys=list(final_dict[0].keys())
		start = 0
		for i in range(len(final_dict)-1):
			if (final_dict[i]['batch'] != final_dict[i+1]['batch']):
				final_dict_1.append(final_dict[i])
				total = {keys[i]:" " for i in range(9)}
				total['batch'] = "<b style=color:orange;>""Total""</b>"
				total['qty'] =  round(sum(float(final_dict[i]['qty']) for i in range(start,i+1)),2)
				total['uri_kg'] =  round(sum(float(final_dict[i]['uri_kg']) for i in range(start,i+1)),2)
				total['uri_nos'] =  round(sum(float(final_dict[i]['uri_nos']) for i in range(start,i+1)),2)
				total['copra'] =  round(sum(float(final_dict[i]['copra']) for i in range(start,i+1)),2)
				total['copra_percent'] =  round(sum(float(final_dict[i]['copra_percent']) for i in range(start,i+1)),2)
				total['shell'] =  round(sum(float(final_dict[i]['shell']) for i in range(start,i+1)),2)
				total['husk'] =  round(sum(float(final_dict[i]['husk']) for i in range(start,i+1)),2)
				total['purchase_amt'] =  round(sum(float(final_dict[i]['purchase_amt']) for i in range(start,i+1)),2)
				total['sales_amt'] =  round(sum(float(final_dict[i]['sales_amt']) for i in range(start,i+1)),2)
				total['wages'] =  round(sum(float(final_dict[i]['wages']) for i in range(start,i+1)),2)
				total['profit'] =  round(sum(float(final_dict[i]['profit']) for i in range(start,i+1)),2)
				total['stock_in_hand'] = round(sum(float(final_dict[i]['stock_in_hand']) for i in range(start,i+1)),2)
				final_dict_1.append(total)
				start = i+1	
			else:
				final_dict_1.append(final_dict[i])
				
		final_dict_1.append(final_dict[-1])
		total = {keys[i]:" " for i in range(9)}
		total['batch'] = "<b style=color:orange;>""Total""</b>"
		total['qty'] = round(sum(float(final_dict[i]['qty']) for i in range(start,len(final_dict))),2)
		total['uri_kg'] = round(sum(float(final_dict[i]['uri_kg']) for i in range(start,len(final_dict))),2)
		total['uri_nos'] = round(sum(float(final_dict[i]['uri_nos']) for i in range(start,len(final_dict))),2)
		total['copra'] = round(sum(float(final_dict[i]['copra']) for i in range(start,len(final_dict))),2)
		total['copra_percent'] = round(sum(float(final_dict[i]['copra_percent']) for i in range(start,len(final_dict))),2)
		total['shell'] = round(sum(float(final_dict[i]['shell']) for i in range(start,len(final_dict))),2)
		total['husk'] = round(sum(float(final_dict[i]['husk']) for i in range(start,len(final_dict))),2)
		total['purchase_amt'] = round(sum(float(final_dict[i]['purchase_amt']) for i in range(start,len(final_dict))),2)
		total['sales_amt'] = round(sum(float(final_dict[i]['sales_amt']) for i in range(start,len(final_dict))),2)
		total['wages'] = round(sum(float(final_dict[i]['wages']) for i in range(start,len(final_dict))),2)
		total['profit'] = round(sum(float(final_dict[i]['profit']) for i in range(start,len(final_dict))),2)
		total['stock_in_hand'] = round(sum(float(final_dict[i]['stock_in_hand']) for i in range(start,len(final_dict))),2)
		final_dict_1.append(total)
	return final_dict_1


def supplier_ratio(batch_qty, batch_supplier_qty):
	batch_supplier_ratio={}
	for bat in batch_supplier_qty:
		if(bat not in batch_supplier_ratio):
			batch_supplier_ratio[bat]={}
		for sup in batch_supplier_qty[bat]:
			add=True
			if(sup in batch_supplier_ratio[bat]):
					add=False
			if(add):
				batch_supplier_ratio[bat][sup]=0
			batch_supplier_ratio[bat][sup]+=(batch_supplier_qty[bat][sup][0]/batch_qty[bat]*100)
				
	return batch_supplier_ratio



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



def get_columns(filters):
	columns=[
		{
			'label': _("Supplier"),
			'fieldname':'supplier',
			'fieldtype':'Link',
			'options':'Supplier',
			'width':120
		},
		{
			'label': _("Item Name"),
			'fieldname':'item_name',
			'fieldtype':'Link',
			'options':'Item',
			'width':120
		},
		{
			'label': _("Lot No"),
			'fieldname':'batch',
			'fieldtype':'Data',
			'width':120
		},
		{
			'label': _("Total Qty"),
			'fieldname':'qty',
			'fieldtype':'Data',
			'width':120
		},
		{
			'label': _("Urithengai Qty (Kg)"),
			'fieldname':'uri_kg',
			'fieldtype':'Data',
			'width':150
		},
		{
			'label': _("Urithengai Qty (Nos)"),
			'fieldname':'uri_nos',
			'fieldtype':'Data',
			'width':160
		},
		{
			'label': _("Copra (kg)"),
			'fieldname':'copra',
			'fieldtype':'Data',
			'width':150
		},
		{
			'label': _("Outtan"),
			'fieldname':'copra_percent',
			'fieldtype':'Percent',
			'width':150
		},
		{
			'label': _("Shell"),
			'fieldname':'shell',
			'fieldtype':'Data',
			'width':120
		},
		{
			'label': _("Husk"),
			'fieldname':'husk',
			'fieldtype':'Data',
			'width':120
		},
		{
			'label': _("Sales Amount"),
			'fieldname':'sales_amt',
			'fieldtype':'Currency',
			'width':120
		},
		{
			'label': _("Stock in Hand"),
			'fieldname':'stock_in_hand',
			'fieldtype':'Currency',
			'width':150,
		},
		{
			'label': _("Purchase Amount"),
			'fieldname':'purchase_amt',
			'fieldtype':'Currency',
			'width':150
		},
		{
			'label': _("Wages"),
			'fieldname':'wages',
			'fieldtype':'Currency',
			'width':120
		},
		{
			'label': _("Profit Amount"),
			'fieldname':'profit',
			'fieldtype':'Currency',
			'width':150,
		}		
	]
	return columns