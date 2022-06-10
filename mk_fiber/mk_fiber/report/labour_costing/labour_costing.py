import frappe
from frappe import _

def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	employee = filters.get("employee_name")	
	filters={'docstatus':1}
	ld_filters={'docstatus':1}
	if(from_date and to_date):
		filters['posting_date']=['between', [from_date, to_date]]
	if(employee):
		ld_filters['labour_name']=employee


	ld=frappe.get_all('Labour Details', filters=ld_filters, pluck='name')
	parent_types=list(set(frappe.get_all('Labour Details', filters=ld_filters, pluck='parenttype')))
	parent_docs=[]
	for doctype in parent_types:
		parent_docs+=frappe.get_all(doctype, filters=filters, pluck='name')
	report_data=[]
	for doc in ld:
		doc=frappe.get_doc('Labour Details', doc)
		if(doc.parent in parent_docs):
			report_data.append([
				doc.labour_name,
				doc.working__process,
				doc.total_count,
				doc.cost_per_piece,
				doc.total_cost,
				doc.paid_amount,
				doc.total_cost - doc.paid_amount
			])



	data = [list(i) for i in report_data]
	emp=[frappe.get_all("Employee",fields=['employee_name'],filters={'name':i[0]})[0]['employee_name'] for i in data]
	for i in range(len(emp)):data[i][0] = str(emp[i])
	final_data = []
	if(len(data)):
		for i in range(len(data)-1):
			if(i<=len(data)):
				final_data.append(data[i])
		final_data.append(data[-1])
		total = [" " for i in range(9)]
		total[0] = "<b style=color:Red;>""Total""</b>"
		total[2] = sum(data[i][2] for i in range(len(data)))
		total[3] = round(sum(data[i][3] for i in range(len(data))) / len(data),2)
		total[4] = sum(data[i][4] for i in range(len(data)))
		total[5] = sum(data[i][5] for i in range(len(data)))
		total[6] = sum(data[i][6] for i in range(len(data)))
		final_data.append(total)
	columns = get_columns()
	return columns, final_data
def get_columns():
	columns = [
		_("Labour Name") + ":Link/Employee:130",
		_("Process") + ":Labour Details:150",
		_("Total Count") + ":int/Labour Details:100",
		_("Cost Per Piece") + ":Curreny:180",
		_("Total Cost") + ":Currency:120",
		_("Paid Amount") + ":Currency:120",
		_("Balance Amount") + ":Currency:150",
		]
	
	return columns