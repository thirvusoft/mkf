var main_data
frappe.ui.form.on("Delivery Note",{
	onload:function(frm,cdt,cdn){
		main_data=locals[cdt][cdn]
		if(main_data.ts_landed_cost_voucher_table){
			if(main_data.ts_duplicate==1){
				if(cur_frm.is_new()){
					frm.clear_table("ts_landed_cost_voucher_table")
					frm.set_value("cost_center","")
					frm.set_value("ts_total_amount","")
					frm.set_value("ts_distribute_charges_based_on","Qty")
				}
			}
			else{
				var landed_table=main_data.ts_landed_cost_voucher_table
				for(var i=0;i<landed_table.length;i++){
					if(main_data.items){
						var items=main_data.items
						for(var j=0;j<items.length;j++){
							if(main_data.items[j].sales_invoice){
								frm.set_value("ts_duplicate",1)
								i=landed_table.length
								break
							}
						}
					}
				}
			}
		}
	},
    validate:function(frm){
		frm.set_value("ts_duplicate",1)
	},
	setup:function(frm){
		frm.set_query("ts_account","ts_landed_cost_voucher_table", function(frm) {
			return {
				filters: {"company":frm.doc.company}
			}
		})
		frm.set_query("ts_expence_account","ts_landed_cost_voucher_table", function() {
			return {
				filters: {"company":frm.doc.company}
			}
		})
		frm.set_query("ts_payment_account_head","ts_landed_cost_voucher_table", function() {
			return {
				filters: {"company":frm.doc.company}
			}
		})
	},
	before_submit: function(frm){
		let total=cur_frm.doc.ts_total_amount?cur_frm.doc.ts_total_amount:0
		for(let item=0;item<cur_frm.doc.items.length;item++){
			let cdt=cur_frm.doc.items[item].doctype
			let cdn=cur_frm.doc.items[item].name
			let data=locals[cdt][cdn]
			frappe.model.set_value(cdt, cdn, 'ts_additional_cost', (data.qty/cur_frm.doc.total_qty)*total)
		}
	}
})

function cost(frm,cdt,cdn){
    let row=locals[cdt][cdn]
    frappe.model.set_value(cdt,cdn,'ts_amount',row.ts_total_count*row.ts_cost_per_price)
}

frappe.ui.form.on("TS Landed Cost Voucher Mk",{
	ts_make_journal_entry:function(frm,cdt,cdn){
		var ts_data=locals[cdt][cdn]
		var ts_total_amount=ts_data.ts_amount
		frappe.model.set_value(cdt,cdn,"ts_createing_je",1)
		var d = new frappe.ui.Dialog({
			title: "Make Journal Entry",
			fields: [
				{label:'Mode of Payment',fieldname:'ts_mode_of_payment',fieldtype:'Link',options: 'Mode of Payment',reqd:1},
				{label:'Payment Account Head',fieldname:'ts_payment_account_head',fieldtype:'Link',options: 'Account',reqd:1,filters:{"company":frm.doc.company}},
				{label:'Paying Amount',fieldname:'ts_paying_amount',fieldtype:'Currency',default:ts_total_amount ,reqd:1},
				{label:'Status',fieldname:'ts_status',fieldtype:'Select',options: ["Draft","Submit"],reqd:1}
			],
			primary_action_label: "Submit",
			primary_action:function(data){
				frappe.model.set_value(cdt, cdn, "ts_mode_of_payment", data.ts_mode_of_payment)
				frappe.model.set_value(cdt, cdn, "ts_status", data.ts_status)
				frappe.model.set_value(cdt, cdn, "ts_payment_account_head", data.ts_payment_account_head)
				frappe.model.set_value(cdt, cdn, "ts_paying_amount", data.ts_paying_amount)
				d.hide()  
			}
		})
		d.show()
	},
	ts_paying_amount:function(frm,cdt,cdn){
		var ts_data=locals[cdt][cdn]
		var ts_remainig_amount=ts_data.ts_amount-ts_data.ts_paying_amount
		frappe.model.set_value(cdt, cdn, "ts_remaining_amount_to_be_paid", ts_remainig_amount)

	},
	ts_account:function(frm,cdt,cdn){
		var ts_data=locals[cdt][cdn]
		var ts_account_type=ts_data.ts_account
		ts_account_type = ts_account_type.split(" ");
		if(ts_account_type[0]=="Creditors"){
			frappe.model.set_value(cdt, cdn, "ts_party_type", "Employee")
		}
		else if(ts_account_type[0]=="Debtors"){
			frappe.model.set_value(cdt, cdn, "ts_party_type", "Customer")
		}
		else{
			frappe.model.set_value(cdt, cdn, "ts_party_type", "")
		}
	},
	ts_party_type:function(frm,cdt,cdn){
		var ts_data=locals[cdt][cdn]
		if(ts_data.ts_party_type=="Supplier"){
			frappe.model.set_value(cdt, cdn, "ts_party_name", main_data.supplier)
		}
		else{
			frappe.model.set_value(cdt, cdn, "ts_party_name", "")
		}
	},
    ts_total_count:function(frm,cdt,cdn){
        cost(frm,cdt,cdn);
    },
    ts_cost_per_price:function(frm,cdt,cdn){
        cost(frm,cdt,cdn);
    }
})