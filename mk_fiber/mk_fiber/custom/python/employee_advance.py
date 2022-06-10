import frappe

def create_employee_advance(doc,action):
    company_list = frappe.get_all("Company",pluck = 'name')
    for lis in company_list:
        new_lis = frappe.get_doc("Company",lis)
        if new_lis.default_employee_advance_account:
            advance_acc = new_lis.default_employee_advance_account
        else:
            frappe.throw("Set Default Employee Advance Account")
    for row in doc.labour_details:
        if(row.paid_amount):
            new_doc = frappe.new_doc("Employee Advance")
            new_doc.update({
                'employee': row.labour_name,
                'exchange_rate': "1",
                'purpose':row.working__process,
                'advance_amount': row.paid_amount,
                'advance_account': advance_acc
            })
            new_doc.insert()
            new_doc.submit()