import frappe
from string import ascii_uppercase
import itertools
def iter_all_strings():
			for size in itertools.count(1):
				for s in itertools.product(ascii_uppercase, repeat=size):
					yield "".join(s)
def autoname(self,event):
    if(self.reference_doctype=="Stock Entry"):
        doc=frappe.get_doc('Stock Entry', self.reference_name)
        if(doc.stock_entry_type=='Repack'):
            batch_name=''
            for row in doc.items:
                if(row.s_warehouse):
                    batch_name=row.batch_no
            if(batch_name):
                p_batch=frappe.get_value('Batch', batch_name, 'parent_batch_id')
                if(p_batch):
                    batch_name=p_batch
                if(not frappe.db.sql("select * from `tabSeries` where name=%s ",batch_name)):
                    frappe.db.sql("INSERT INTO `tabSeries` (`name`, `current`) VALUES (%s, 0)", batch_name)
                frappe.db.sql("UPDATE `tabSeries` SET `current` = `current` + 1 where name=%s",batch_name)
                self.name=batch_name+'-'+str(frappe.db.sql("select `current` from `tabSeries` where name=%s ",batch_name)[0][0])
        return
    
    max_series=150
    series = []
    for s in iter_all_strings():
        series.append(s)
        if s == 'ZZ':
            break
    try:
        frappe.db.sql("ALTER TABLE tabSeries ADD doctype varchar(20) NULL;")
        frappe.db.sql("ALTER TABLE tabSeries ADD is_default varchar(10) NULL;")
    except:
        pass
    if(not frappe.db.sql("select * from `tabSeries` where is_default = 1 and doctype = 'Batch' ")):
        frappe.db.sql("INSERT INTO `tabSeries` (`name`, `current`,`doctype`,`is_default`) VALUES (%s, 0, 'Batch', 1)",series[0])
    
    elif(frappe.db.sql("select `current` from `tabSeries` where is_default = 1 and doctype = 'Batch' ")[0][0] > max_series-1):
        last_series = frappe.db.sql("select `name` from `tabSeries` where is_default = 1 and doctype = 'Batch' ")[0][0]
        frappe.db.sql("UPDATE `tabSeries` SET `is_default` = 0 where is_default = 1 and doctype = 'Batch'")
        series_1 = series[series.index(last_series)+1]
        frappe.db.sql("INSERT INTO `tabSeries` (`name`, `current`,`doctype`,`is_default`) VALUES (%s, 0, 'Batch', 1)",series_1)
    frappe.db.sql("UPDATE `tabSeries` SET `current` = `current` + 1 where is_default = 1 and doctype = 'Batch'")
    doc_series = frappe.db.sql("select `current` from `tabSeries` where is_default = 1 and doctype = 'Batch' ")[0][0]
    doc_name = frappe.db.sql("select `name` from `tabSeries` where is_default = 1 and doctype = 'Batch' ")[0][0]
    self.name = doc_name + "{0:0=3d}".format(doc_series)