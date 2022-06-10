import frappe
from frappe.utils import flt
from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import get_stock_balance_for
def creating_stock_reconciliation(document,action):
    ts_landed_cost_voucher_table=document.ts_landed_cost_voucher_table
    if(ts_landed_cost_voucher_table):
        ts_stock_re_count=0
        ts_expence_head=[]
        ts_head_wise_total=[]
        for i in range(0,len(ts_landed_cost_voucher_table),1):
            if(ts_landed_cost_voucher_table[i].ts_expence_account not in ts_expence_head):
                ts_expence_head.append(ts_landed_cost_voucher_table[i].ts_expence_account)
                ts_tot_amt=0
                for j in range(0,len(ts_landed_cost_voucher_table),1):
                    if(ts_landed_cost_voucher_table[i].ts_expence_account==ts_landed_cost_voucher_table[j].ts_expence_account):
                        ts_tot_amt+=ts_landed_cost_voucher_table[j].ts_amount
                ts_head_wise_total.append(ts_tot_amt)
        for e in range (0,len(ts_expence_head),1):
            if ts_stock_re_count==0:
                ts_items=[]
                separte_values=calculating_landed_cost_voucher_amount(document,ts_head_wise_total[e])
                for item in document.get('items'):
                    for v in range(0,len(separte_values[0]),1):
                        if separte_values[0][v]==item.item_code:
                            ts_valuation_rate=separte_values[1][v]
                    if item.t_warehouse:
                        ts_valuation_rate=ts_valuation_rate/item.qty
                        ts_items.append({
                            "item_code":item.item_code,
                            "warehouse":item.t_warehouse,
                            "batch_no":item.batch_no,
                            'qty':item.qty,
                            "current_qty":item.qty,
                            "valuation_rate":ts_valuation_rate+ item.basic_rate,
                            "amount":item.qty*ts_valuation_rate+ item.basic_rate,
                            "current_valuation_rate": item.basic_rate,
                            "current_amount":item.basic_amount,
                            "amount_difference":(item.qty*ts_valuation_rate+ item.basic_rate)-item.basic_amount,
                        })
                ts_creator=frappe.get_doc({
                    "doctype":"Stock Reconciliation",
                    "purpose":"Stock Reconciliation",
                    "items":ts_items,
                    "expense_account":ts_expence_head[e],
                    "cost_center":document.cost_center,
                    "ts_stock_entry_no":document.name,
                    
                })
                ts_stock_re_count+=1
                ts_creator.save()
                ts_creator.submit()
                previous_doc=ts_creator
            else:
                separte_values=calculating_landed_cost_voucher_amount(document,ts_head_wise_total[e])
                # old_doc=len(previous_doc.items)
                old_it=0
                ts_items=[]
                for item in document.get('items'):
                    for v in range(0,len(separte_values[0]),1):
                        if separte_values[0][v]==item.item_code:
                            ts_valuation_rate=separte_values[1][v]
                    if item.t_warehouse:
                        ts_valuation_rate=ts_valuation_rate/item.qty
                        ts_items.append({
                            "item_code":item.item_code,
                            "warehouse":item.t_warehouse,
                            "batch_no":item.batch_no,
                            'qty':item.qty,
                            "current_valuation_rate": previous_doc.items[old_it].valuation_rate,
                            "current_amount":previous_doc.items[old_it].amount,
                            "current_qty":item.qty,
                            "valuation_rate":ts_valuation_rate+ previous_doc.items[old_it].valuation_rate,
                            "amount":item.qty*ts_valuation_rate+ previous_doc.items[old_it].valuation_rate,
                            "amount_difference":(item.qty*ts_valuation_rate+ previous_doc.items[old_it].current_valuation_rate)-previous_doc.items[old_it].current_amount        
                        })
                        old_it+=1
                    
                ts_creator=frappe.get_doc({
                    "doctype":"Stock Reconciliation",
                    "purpose":"Stock Reconciliation",
                    "items":ts_items,
                    "expense_account":ts_expence_head[e],
                    "cost_center":document.cost_center,
                    "ts_stock_entry_no":document.name
                })
                ts_stock_re_count+=1
                ts_creator.save()
                ts_creator.submit()
                previous_doc=ts_creator


def calculating_landed_cost_voucher_amount(self,value):
    total_item_cost = 0.0
    total_charges = 0.0
    item_count = 0
    ts_item_code=[]
    ts_separate_amount=[]
    based_on_field = frappe.scrub(self.ts_distribute_charges_based_on)
    for item in self.get('items'):
        if item.t_warehouse:
            total_item_cost += item.get(based_on_field)
    for item in self.get('items'):
        if item.t_warehouse:
            ts_total_value = flt(flt(item.get(based_on_field)) * (flt(value) / flt(total_item_cost)),
                )
            total_charges += ts_total_value
            item_count += 1
            ts_item_code.append(item.item_code)
            ts_separate_amount.append(ts_total_value)
    return ts_item_code,ts_separate_amount


def calculating_difference_value(document,event):
    if document.items:
        ts_diff_amount=0
        for item in document.items:
            ts_diff_amount+=item.amount_difference
        document.difference_amount=ts_diff_amount
