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
        if(ts_data.ts_extra_charges){
        for(var i=0;i<(ts_data.ts_extra_charges?ts_data.ts_extra_charges:[]).length;i++){
            ts_total_amount=ts_total_amount+ts_data.ts_extra_charges[i].ts_amount
        }
        frm.clear_table("ts_additional_cost")
        var ts_new_row=frm.add_child("ts_additional_cost");
        ts_new_row.expense_account="Expenses Included In Valuation - MF",
        ts_new_row.description=cur_frm.doc.doctype
        ts_new_row.base_amount=ts_total_amount
        ts_new_row.exchange_rate=ts_total_amount
        ts_new_row.amount=ts_total_amount
        refresh_field("ts_additional_cost");
    }
    }
})

function cost(frm,cdt,cdn){
    let row=locals[cdt][cdn]
    frappe.model.set_value(cdt,cdn,'total_cost',row.total_count*row.cost_per_piece)
}
frappe.ui.form.on('Labour Details',{
total_count:function(frm,cdt,cdn){
    cost(frm,cdt,cdn);
},
cost_per_piece:function(frm,cdt,cdn){
    cost(frm,cdt,cdn);
}
})
frappe.ui.form.on('Purchase Receipt',{
    onload:function(frm){
        cur_frm.refresh();
    }
})

frappe.ui.form.on("Purchase Receipt",{
    before_save:function(frm,cdt,cdn){
        var ts_data=locals[cdt][cdn]
        if(ts_data.supplier){
            var ts_total_amount=0
            for(var i=0;i<(ts_data.labour_details?ts_data.labour_details:[]).length;i++){
                ts_total_amount=ts_total_amount+ts_data.labour_details[i].total_cost
            }
            frm.clear_table("ts_additional_cost")
            var ts_new_row=frm.add_child("ts_additional_cost");
            ts_new_row.expense_account="Expenses Included In Valuation - MF",
            ts_new_row.description=cur_frm.doc.doctype
            ts_new_row.amount=ts_total_amount
            ts_data.total_additional_costs = ts_total_amount
            refresh_field("ts_additional_cost");
        }
    }
})