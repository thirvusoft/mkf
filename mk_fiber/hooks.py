from . import __version__ as app_version

app_name = "mk_fiber"
app_title = "Mk Fiber"
app_publisher = "mk"
app_description = "mk"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "mk"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/mk_fiber/css/mk_fiber.css"
# app_include_js = "/assets/mk_fiber/js/mk_fiber.js"

# include js, css files in header of web template
# web_include_css = "/assets/mk_fiber/css/mk_fiber.css"
# web_include_js = "/assets/mk_fiber/js/mk_fiber.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "mk_fiber/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {"Stock Entry" : "mk_fiber/custom/js/stockentry.js",
"Purchase Receipt":"mk_fiber/custom/js/purchase_receipt.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "mk_fiber.install.before_install"
# after_install = "mk_fiber.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "mk_fiber.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Employee": {
		# "on_update": "method",
		# "on_cancel": "method",
		# "on_trash": "method",
		"before_save": "mk_fiber.mk_fiber.custom.python.employee.auto_name"
	},
	"Purchase Receipt":{
		"on_submit":"mk_fiber.mk_fiber.custom.python.batch.purchase_receipt"
		},
	"Stock Entry":{
		"on_submit":"mk_fiber.mk_fiber.custom.python.batch.stock_entry"
	},
	"Sales Invoice":{
		"on_submit":"mk_fiber.mk_fiber.custom.python.batch.sales_invoice"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"mk_fiber.tasks.all"
# 	],
# 	"daily": [
# 		"mk_fiber.tasks.daily"
# 	],
# 	"hourly": [
# 		"mk_fiber.tasks.hourly"
# 	],
# 	"weekly": [
# 		"mk_fiber.tasks.weekly"
# 	]
# 	"monthly": [
# 		"mk_fiber.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "mk_fiber.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "mk_fiber.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "mk_fiber.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
	{
		"doctype": "{doctype_1}",
		"filter_by": "{filter_by}",
		"redact_fields": ["{field_1}", "{field_2}"],
		"partial": 1,
	},
	{
		"doctype": "{doctype_2}",
		"filter_by": "{filter_by}",
		"partial": 1,
	},
	{
		"doctype": "{doctype_3}",
		"strict": False,
	},
	{
		"doctype": "{doctype_4}"
	}
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"mk_fiber.auth.validate"
# ]

