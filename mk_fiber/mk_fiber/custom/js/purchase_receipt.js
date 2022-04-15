frappe.ui.form.on("Purchase Receipt",{
    onload:function(frm,cdt,cdn){
        frappe.model.set_value(cdt,cdn,"set_posting_time",1)
        frappe.model.set_value(cdt,cdn,"posting_date","")
        frappe.model.set_value(cdt,cdn,"posting_time","")

    }
})