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
	for i in su:
		cocobatch=[]
		for j in se:
			x=frappe.get_doc('Stock Entry',j.name)
			for g in x.items:
				if g.batch_no==i.name :
					cocobatch.append(*[t.batch_no for t in x.items if(t.item_code=='1002') ])
					continue
				
		batch_wise[i.name]=cocobatch
	uribatch_wise={}
	for l in batch_wise:
		uribatch={'1002':0,'1003':0,'total_qty':0}
		pr=frappe.get_all('Purchase Receipt',{'supplier':frappe.get_value('Batch',l,'supplier')})
		for i in pr:
			prdoc=frappe.get_doc('Purchase Receipt',i.name)
			for item in prdoc.items:
				if(item.batch_no==l):
					uribatch['total_qty']=item.qty
		for i in batch_wise[l]:
			se=frappe.get_all('Stock Entry',{'stock_entry_type':'Repack'})
			for j in se:
				x=frappe.get_doc('Stock Entry',j.name)
				for g in x.items:
					if(g.item_code=='1002' and g.s_warehouse  and g.batch_no==i):
						for t in x.items:
							if(t.item_code=='1002' or t.item_code=='1003'):
								uribatch[t.item_code]+=t.qty
						continue
				
		uribatch_wise[l]=uribatch

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

	
	for i in urithengaibatch:
		uribatch={'1002':0,'1003':0}
		se=frappe.get_all('Stock Entry',{'stock_entry_type':'Repack'})
		for j in se:
			x=frappe.get_doc('Stock Entry',j.name)
			for g in x.items:
				if(g.item_code=='1002' and g.s_warehouse!=''  and g.batch_no==i):
					for t in x.items:
						if(t.item_code=='1002' or t.item_code=='1003'):
							uribatch[t.item_code]+=t.qty
					continue
		urithengaibatch[i].update(uribatch)
	

	uribatch_wise.update(urithengaibatch)





	for i in uribatch_wise:
		data.append({
			'supplier':frappe.get_value('Batch',i,'supplier'),
			'item_code':'1001',
			'batch_no':i,
			'total_qty':uribatch_wise[i]['total_qty'],
			'total_urithengai_qty_(in_nos)':uribatch_wise[i]['1002'],
			'total_paruppu_(in_kg)':uribatch_wise[i]['1003'],
			'paruppu_percentage':round((uribatch_wise[i]['1003']/(uribatch_wise[i]['1002'] or 1)*100)/1 if(uribatch_wise[i]['1002']!=0) else 0 ,2)
		})
	
	return columns,data

