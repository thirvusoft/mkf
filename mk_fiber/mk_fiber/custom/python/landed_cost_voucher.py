import frappe
from erpnext.stock.doctype.landed_cost_voucher.landed_cost_voucher import LandedCostVoucher

@frappe.whitelist()
def creating_landed_cost_voucher(document,action):
    try:
        if document.update_stock==1:
            ts_start=1
        else:
            ts_start=0
    except:
        ts_start=1

    if ts_start==1:
        ts_landed_cost_voucher_table=document.ts_landed_cost_voucher_table
        if(ts_landed_cost_voucher_table):
            ts_charges=[]
            for i in range(0,len(ts_landed_cost_voucher_table),1):
                if ts_landed_cost_voucher_table[i].ts_description:
                    ts_description=ts_landed_cost_voucher_table[i].ts_description
                else:
                    ts_description=ts_landed_cost_voucher_table[i].ts_expence_account
                ts_charges.append({
                    "expense_account":ts_landed_cost_voucher_table[i].ts_expence_account                     ,
                    "description":ts_description,
                    "amount":ts_landed_cost_voucher_table[i].ts_amount
                })
            ts_creator=frappe.get_doc({
                "doctype":"Landed Cost Voucher",
                "purchase_receipts":[{
                    'receipt_document_type':document.doctype,
                    "receipt_document":document.name,
                    "company":document.company,
                    "supplier":document.supplier,
                    "grand_total":document.grand_total
                }],
                "taxes":ts_charges,
                "distribute_charges_based_on":document.ts_distribute_charges_based_on
            })
            ts_creator.get_items_from_purchase_receipts()
            ts_creator.insert()
            ts_creator.submit()

def total_amount_calculator(document,action):
    ts_total_amount=0
    ts_landed_cost_voucher_table=document.ts_landed_cost_voucher_table
    if(ts_landed_cost_voucher_table):
        for i in range(0,len(ts_landed_cost_voucher_table),1):
            ts_total_amount+=ts_landed_cost_voucher_table[i].ts_amount
        document.ts_total_amount=ts_total_amount
        
def creating_journal_entry(document,action):
    ts_landed_cost_voucher_table=document.ts_landed_cost_voucher_table
    if(ts_landed_cost_voucher_table):
        for i in range(0,len(ts_landed_cost_voucher_table),1):
            if not ts_landed_cost_voucher_table[i].ts_journal_entry:
                if not document.cost_center:
                    frappe.throw('Please Select Cost Center')
                if(ts_landed_cost_voucher_table[i].ts_createing_je == 0):
                    if ts_landed_cost_voucher_table[i].ts_party_type:
                        ts_landed_cost_voucher_table[i].ts_remaining_amount_to_be_paid=ts_landed_cost_voucher_table[i].ts_expence_account
                        ts_creator=frappe.get_doc({
                                "doctype":"Journal Entry",
                                "company":document.company,
                                "ts_source_doctype_name":document.doctype,
                                "ts_purchase_receipt_invoice_no":document.name,
                                "posting_date":document.posting_date,
                                "accounts":[{
                                    "account":ts_landed_cost_voucher_table[i].ts_expence_account,
                                    "debit_in_account_currency":ts_landed_cost_voucher_table[i].ts_amount,
                                    "cost_center":document.cost_center
                                },{
                                    "account":ts_landed_cost_voucher_table[i].ts_account,
                                    "party_type":ts_landed_cost_voucher_table[i].ts_party_type,
                                    "party":ts_landed_cost_voucher_table[i].ts_party_name,
                                    "credit_in_account_currency":ts_landed_cost_voucher_table[i].ts_amount
                                    }],
                            })
                        ts_creator.insert()
                        ts_landed_cost_voucher_table[i].ts_journal_entry=ts_creator.name
                        document.submit()
                        ts_creator.submit()
                    else:
                        ts_creator=frappe.get_doc({
                                "doctype":"Journal Entry",
                                "company":document.company,
                                "ts_source_doctype_name":document.doctype,
                                "ts_purchase_receipt_invoice_no":document.name,
                                "posting_date":document.posting_date,
                                "accounts":[{
                                    "account":ts_landed_cost_voucher_table[i].ts_expence_account,
                                    "debit_in_account_currency":ts_landed_cost_voucher_table[i].ts_amount,
                                    "cost_center":document.cost_center
                                },{
                                    "account":ts_landed_cost_voucher_table[i].ts_account,
                                    "credit_in_account_currency":ts_landed_cost_voucher_table[i].ts_amount
                                    }],
                            })
                        ts_creator.insert()
                        ts_landed_cost_voucher_table[i].ts_journal_entry=ts_creator.name
                        document.submit()
                        ts_creator.submit()

                elif(ts_landed_cost_voucher_table[i].ts_createing_je == 1):
                    if ts_landed_cost_voucher_table[i].ts_amount<ts_landed_cost_voucher_table[i].ts_paying_amount:
                        frappe.throw("Paying Amount Should Not Be Greater Then Total Amount In Landed Cost Voucher Table")
                    if(ts_landed_cost_voucher_table[i].ts_amount!=ts_landed_cost_voucher_table[i].ts_paying_amount):
                        ts_landed_cost_voucher_table[i].ts_remaining_amount_to_be_paid=(ts_landed_cost_voucher_table[i].ts_amount-ts_landed_cost_voucher_table[i].ts_paying_amount)
                    ts_creator=frappe.get_doc({
                        "doctype":"Journal Entry",
                        "company":document.company,
                        "ts_source_doctype_name":document.doctype,
                        "ts_purchase_receipt_invoice_no":document.name,
                        "posting_date":document.posting_date,
                        'mode_of_payment':ts_landed_cost_voucher_table[i].ts_mode_of_payment,
                        "accounts":[{
                            "account":ts_landed_cost_voucher_table[i].ts_expence_account,
                            "debit_in_account_currency":ts_landed_cost_voucher_table[i].ts_amount,
                            "cost_center":document.cost_center
                        },
                        {
                            "account":ts_landed_cost_voucher_table[i].ts_account,
                            "party_type":ts_landed_cost_voucher_table[i].ts_party_type,
                            "party":ts_landed_cost_voucher_table[i].ts_party_name,
                            "credit_in_account_currency":ts_landed_cost_voucher_table[i].ts_amount
                        },
                        {
                            "account":ts_landed_cost_voucher_table[i].ts_payment_account_head,
                            "credit_in_account_currency":ts_landed_cost_voucher_table[i].ts_paying_amount
                        },
                        {
                            "account":ts_landed_cost_voucher_table[i].ts_account,
                            "party_type":ts_landed_cost_voucher_table[i].ts_party_type,
                            "party":ts_landed_cost_voucher_table[i].ts_party_name,
                            "debit_in_account_currency":ts_landed_cost_voucher_table[i].ts_paying_amount,
                        }],
                    })
                    ts_creator.insert()
                    ts_landed_cost_voucher_table[i].ts_journal_entry=ts_creator.name
                    ts_landed_cost_voucher_table[i].ts_paid_amount=ts_landed_cost_voucher_table[i].ts_paying_amount
                    document.submit()
                    if(ts_landed_cost_voucher_table[i].ts_status=="Draft"):
                        ts_creator.save()
                    else:
                        ts_creator.submit()

def removing_journal_entry(document,action):
    ts_landed_cost_voucher_table=document.ts_landed_cost_voucher_table
    if(ts_landed_cost_voucher_table):
        ts_items=document.items
        ts_count=0
        if ts_items:
            for item in ts_items:
                try:
                    if item.purchase_receipt:
                       ts_count=1
                except:
                    pass
        if ts_count==0:
            for i in range(0,len(ts_landed_cost_voucher_table),1):
                ts_landed_cost_voucher_table[i].ts_journal_entry=""
