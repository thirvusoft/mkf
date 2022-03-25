from asyncio import constants
import frappe
from frappe import _


# def execute(filters=None):
# 	print(filters)
# 	columns, data = [] , []
# 	columns = get_columns()
# 	repack_items = frappe.get_list('Stock Entry Detail', {'item_code', 'item_name', 'qty', 'batch_no', 'parent'})

# 	print(repack_items)
# 	print(frappe.get_list('Stock Entry Detail', {'item_code', 'item_name', 'qty', 'batch_no', 'parent'}))
# 	pr_items = frappe.get_list('Purchase Receipt Item', {'item_code', 'item_name', 'qty', 'batch_no', 'parent'})
# 	final_data = []
# 	for row in pr_items:
# 		purchase_item_wise_se_list = frappe.get_list('Stock Entry Detail', {'item_code':row['item_code'], 'batch_no':row['batch_no']},['parent'])
# 		total_paruppu_qty = 0
# 		total_urithengai_qty = 0
# 		for row1 in purchase_item_wise_se_list:
# 			print(frappe.get_list('Stock Entry Detail', {'item_code':'1003'}, ['qty'],pluck='qty'))
# 			print(frappe.get_list('Stock Entry Detail', {'item_code':'1002','t_warehouse':None},['t_warehouse']))
# 			total_paruppu_qty += sum(frappe.get_list('Stock Entry Detail', {'item_code':'1003'}, ['qty'],pluck='qty'))
# 			total_urithengai_qty += sum(frappe.get_list('Stock Entry Detail', {'item_code':'1002'}, ['qty'],pluck='qty'))	
# 			print(total_urithengai_qty)
# 		final_data.append({'supplier':frappe.db.get_value('Purchase Receipt', row['parent'], 'supplier'), 
# 							'item_code':row['item_code'],
# 							'item_name':row['item_name'],
# 							'batch_no':row['batch_no'],
# 							'total_qty':row['qty'],
# 							'total_urithengai_qty': total_urithengai_qty,
# 							'total_paruppu_qty': total_paruppu_qty,
# 							'profit_percentage':(total_paruppu_qty/row['qty'])*100 if total_paruppu_qty else 0})


# 	return columns, final_data


def get_columns():
	columns = [
		_("Supplier") + ":Link/Supplier:150",
		_("Item Code") + ":Link/Item:150",
		_("Batch No") + "::150",
		_("Total Qty") + "::150",
		_("Total Urithengai Qty") + "::150",
		_("Total Paruppu Qty") + "::180",
		_("Profit Percentage") + "::150"
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
			'total_urithengai_qty':uribatch_wise[i]['1002'],
			'total_paruppu_qty':uribatch_wise[i]['1003'],
			'profit_percentage':round((uribatch_wise[i]['1003']/(uribatch_wise[i]['1002'] or 1)*100)/1 if(uribatch_wise[i]['1002']!=0) else 0 ,2)
		})
	return columns,data

