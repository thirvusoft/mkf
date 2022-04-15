frappe.ui.form.on("Purchase Receipt",{
    onload:function(frm,cdt,cdn){
        if(cur_frm.is_new()==1){
            frappe.model.set_value(cdt,cdn,"set_posting_time",1)
            frappe.model.set_value(cdt,cdn,"posting_date","")
            frappe.model.set_value(cdt,cdn,"posting_time","")
        }
    }
})

frappe.ui.form.on("Purchase Receipt",{
    before_save:function(frm,cdt,cdn){
        var ts_data=locals[cdt][cdn]
        var ts_total_amount=0
        for(var i=0;i<ts_data.ts_extra_charges.length;i++){
            ts_total_amount=ts_total_amount+ts_data.ts_extra_charges[i].ts_amount
        }
        frm.clear_table("ts_additional_cost")
        var ts_new_row=frm.add_child("ts_additional_cost");
        ts_new_row.expense_account="Expenses Included In Valuation - Ts",
        ts_new_row.description="Purchase Receipt"
        ts_new_row.base_amount=ts_total_amount
        ts_new_row.exchange_rate=ts_total_amount
        ts_new_row.amount=ts_total_amount
        refresh_field("ts_additional_cost");
    }
})