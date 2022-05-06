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
        new_doc = frappe.new_doc("Employee Advance")
        new_doc.update({
            'employee': row.labour_name,
            'exchange_rate': "1",
            'purpose':row.working_process,
            'advance_amount': row.paid_amount,
            'advance_account': advance_acc
        })
        new_doc.insert()
        new_doc.submit()
def create_payment_entry(doc,action):
        add_doc=frappe.new_doc('Payment Entry')
        add_doc.payment_type='Pay'
        add_doc.party_type = 'Employee'
        add_doc.party = doc.employee
        add_doc.posting_date = doc.posting_date
        add_doc.posting_date = doc.posting_date
        add_doc.paid_from_account_currency = doc.currency
        add_doc.mode_of_payment = doc.mode_of_payment
        add_doc.paid_amount=doc.advance_amount
        add_doc.received_amount=doc.advance_amount
        add_doc.source_exchange_rate=1.0
        add_doc.target_exchange_rate=1.0
        add_doc.paid_to=doc.advance_account
        add_doc.paid_from=doc.advance_account
        add_doc.append(
		"references",
		{
                        "reference_doctype": 'Employee Advance',
                        "reference_name": doc.name,
                        "total_amount": doc.advance_amount,
                        "outstanding_amount": doc.advance_amount,
                        "allocated_amount": doc.advance_amount,
                },
        )

        add_doc.insert()
        add_doc.submit()        
        frappe.db.commit()