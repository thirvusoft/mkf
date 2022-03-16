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