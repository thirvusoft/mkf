import frappe
from frappe import _

def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	employee = filters.get("employee_name")	
		

	conditions = ""
	if from_date or to_date or employee:
		conditions = " where 1=1"
		if from_date and to_date:
			conditions += " and se.posting_date between '{0}' and '{1}' ".format(from_date, to_date)
		
		if employee:
			conditions += " and ld.labour_name ='{0}' ".format(employee)
	report_data = frappe.db.sql("""select ld.labour_name,
										 ld.working__process,
										  ld.total_count,
										  ld.cost_per_piece,
										  ld.total_cost,
										  (ld.total_cost - ld.paid_amount) as total_cost 
								   
								   from `tabLabour Details` as ld
								   left outer join `tabStock Entry` as se on
								   		se.name = ld.parent
								   {0}
								   order by posting_date;
						""".format(conditions))
	
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
		_("Balance Amount") + ":Currency:150"
		]
	
	return columns