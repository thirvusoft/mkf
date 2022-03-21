import frappe
import erpnext
from frappe.model.naming import make_autoname

def auto_name(doc,action):
    doc.name = doc.naming