// Copyright (c) 2016, jyoti and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["PO - Balance Items"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.nowdate(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.nowdate(),
			"reqd": 1,
			"width": "60px"
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			//"reqd": 1,
			"options": ["Draft", "To Deliver and Bill"],
			
		},
		{
			"fieldname": "purchase_order",
			"label": __("Purchase Order"),
			"fieldtype": "Link",
			"options": "Purchase Order",
			//"reqd": 1
		},
		{
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			//"reqd": 1
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			//"reqd": 1
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			//"reqd": 1
		},

	]
};