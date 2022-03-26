import frappe
from frappe import _


def get_columns():
	columns = [
		_("Supplier") + ":Link/Supplier:150",
		_("Item Code") + ":Link/Item:150",
		_("Batch No") + "::150",
		_("Total Qty") + "::150",
		_("Total Urithengai Qty (in NOS)") + "::250",
		_("Total Paruppu (in Kg)") + "::180",
		_("Paruppu Percentage") + "::150"
	]
	return columns

def execute(filters=None):
	columns,data=get_columns(),[]
	start_date=filters['start_date']
	end_date=filters['end_date']
	filter={'item':'1001'}
	if(filters.get('supplier')):
		filter['supplier']=filters['supplier']
	filter['creation']=["between",[start_date,end_date]]
	su=frappe.get_all('Batch',filter,['name','supplier'])
	batch_wise={}
	se=frappe.get_all('Stock Entry',{'stock_entry_type':'Repack'})
	for supplier in su:
		coco_batch=[]
		for stock_entry in se:
			se_doc=frappe.get_doc('Stock Entry',stock_entry.name)
			for se_item in se_doc.items:
				if se_item.batch_no==supplier.name :
					cocobatch.append(*[item.batch_no for item in se_doc.items if(item.item_code=='1002') ])
					continue
				
		batch_wise[supplier.name]=coco_batch
	uribatch_wise={}
	for supplier in batch_wise:
		uri_batch={'1002':0,'1003':0,'total_qty':0}
		pr=frappe.get_all('Purchase Receipt',{'supplier':frappe.get_value('Batch',supplier,'supplier')})
		for purchase_reci in pr:
			prdoc=frappe.get_doc('Purchase Receipt',purchase_reci.name)
			for item in prdoc.items:
				if(item.batch_no==supplier):
					uri_batch['total_qty']=item.qty
		for batch in batch_wise[supplier]:
			for stock_entry in se:
				se_doc=frappe.get_doc('Stock Entry',stock_entry.name)
				for item in se_doc.items:
					if(item.item_code=='1002' and item.s_warehouse  and item.batch_no==batch):
						for se_items in se_doc.items:
							if(se_items.item_code=='1002' or se_items.item_code=='1003'):
								uri_batch[se_items.item_code]+=se_items.qty
						continue
				
		uribatch_wise[supplier]=uri_batch

	# Direct urithengai purchase
	urithengaibatch={}
	filter={'item_code':'1002'}
	if(filters.get('supplier')):
		filter['supplier']=filters['supplier']	
	filter['posting_date']=["between",[start_date,end_date]]
	for pr in frappe.get_all('Purchase Receipt',filter):
		prdoc=frappe.get_doc('Purchase Receipt',pr.name)
		for item in prdoc.items:
			if(item.item_code=='1002'):
				urithengaibatch[item.batch_no]={'total_qty':item.qty}

	
	for batch in urithengaibatch:
		uri_batch={'1002':0,'1003':0}
		for stock_entry in se:
			se_doc=frappe.get_doc('Stock Entry',stock_entry.name)
			for item in se_doc.items:
				if(item.item_code=='1002' and item.s_warehouse!=''  and item.batch_no==batch):
					for se_items in se_doc.items:
						if(se_items.item_code=='1002' or se_items.item_code=='1003'):
							uri_batch[se_items.item_code]+=se_items.qty
					continue
		urithengaibatch[batch].update(uri_batch)
	

	uribatch_wise.update(urithengaibatch)





	for batch in uribatch_wise:
		data.append({
			'supplier':frappe.get_value('Batch',batch,'supplier'),
			'item_code':'1001',
			'batch_no':batch,
			'total_qty':uribatch_wise[batch]['total_qty'],
			'total_urithengai_qty_(in_nos)':uribatch_wise[batch]['1002'],
			'total_paruppu_(in_kg)':uribatch_wise[batch]['1003'],
			'paruppu_percentage':round((uribatch_wise[batch]['1003']/(uribatch_wise[batch]['1002'] or 1)*100)/1 if(uribatch_wise[batch]['1002']!=0) else 0 ,2)
		})
	
	return columns,data

