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
frappe.ui.form.on('Stock Entry',{
    onload:function(frm){
        cur_frm.refresh();
    }
})

frappe.ui.form.on("Stock Entry",{
    before_save:function(frm,cdt,cdn){
        var ts_data=locals[cdt][cdn]
        if(ts_data.stock_entry_type=="Repack"){
            var ts_total_amount=0
            for(var i=0;i<ts_data.labour_details.length;i++){
                ts_total_amount=ts_total_amount+ts_data.labour_details[i].total_cost
            }
            frm.clear_table("additional_costs")
            var ts_new_row=frm.add_child("additional_costs");
            ts_new_row.expense_account="Expenses Included In Valuation - MF",
            ts_new_row.description="Purchase Receipt"
            ts_new_row.amount=ts_total_amount
            refresh_field("additional_costs");
        }
    }
})