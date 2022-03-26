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
	report_data = frappe.db.sql("""select ld.labour_name,ld.working_process,
										  ld.total_count,ld.cost_per_piece,ld.total_cost,
										  (ld.total_cost -(ld.total_count * ld.cost_per_piece)) as total_cost 
								   from `tabLabour Details` as ld
								   left outer join `tabStock Entry` as se on
								   		se.name = ld.parent
								   {0}
								   order by posting_date;
						""".format(conditions))
	
	columns, data = get_columns(), report_data
	return columns, data

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