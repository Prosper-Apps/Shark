// Copyright (c) 2016, jyoti and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["New Sales Cost Report modified"] = {
	"filters": [{
		"fieldname":"company",
		"label": __("Company"),
		"fieldtype": "Link",
		"options": "Company",
		"reqd": 1,
		"default": frappe.defaults.get_user_default("Company")
	},
	{
		"fieldname": "sales_order",
		"label": __("Sales Order"),
		"fieldtype": "Link",
		"options": "Sales Order",
		"reqd": 1,
		"get_query": function() {
			return {
			"doctype": "Sales Order",
			"filters": {
			"docstatus": 1,
			}
			}
			}
	},
	{
		"fieldname":"warehouse",
		"label": __("Warehouse"),
		"fieldtype": "Link",
		"options": "Warehouse",
		"reqd": 1
		
	}
		

	]
}

