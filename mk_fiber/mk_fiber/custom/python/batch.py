import frappe
def purchase_receipt(self,event):
    run=False
    for item in self.items:
        if(item.batch_no and run==False):
            doc=frappe.get_doc('Batch',item.batch_no)
            costing_details= doc.get('ts_costing_details') or []
            cost=0
            for amount in self.ts_additional_cost:
                cost+=(amount.amount or 0)
            pr_costing={'purpose':self.doctype,
                        'cost':cost,
                        'batch':item.batch_no,
                        'doc_name':self.name,
                        'from_pr':1
                        }
            doc.update({
                'ts_costing_details':costing_details+[pr_costing]
            })
            doc.save()
            frappe.db.commit()
            run=True
def stock_entry(self,event):
    for item in self.items:
        if(item.s_warehouse):
            batch = frappe.get_value('Batch',item.batch_no,"parent_batch_id")
            if not batch:
                batch = item.batch_no
            for r_items in self.items:
                if r_items.t_warehouse:
                    doc = frappe.get_doc('Batch',r_items.batch_no)
                    doc.update({
                        "parent_batch_id":batch
                    })
                    doc.save()
            doc = frappe.get_doc('Batch',batch)
            child_batch_details = doc.ts_child_batch_details or []
            for all_item in self.items:
                child_batch_details.append({
                    "t_warehouse":1 if(all_item.t_warehouse) else 0,
                    "s_warehouse":1 if(all_item.s_warehouse) else 0,
                    "item_code":all_item.item_code,
                    "quantity":all_item.qty,
                    "batch_no":all_item.batch_no,
                    "doc_name":all_item.name
                })
            doc.update({
                "ts_child_batch_details":child_batch_details
            })
            costing_details= doc.get('ts_costing_details') or []
            cost=0
            paid_amount=0
            for amount in self.labour_details:
                cost+=(amount.total_cost or 0)
                paid_amount+=(amount.paid_amount)
            pr_costing={'purpose':self.doctype,
                        'cost':cost,
                        'batch':item.batch_no,
                        'doc_name':self.name,
                        'from_se':1,
                        'paid_amount':paid_amount
                        }
            doc.update({
                'ts_costing_details':costing_details+[pr_costing]
            })
            doc.save()
    frappe.db.commit()
            