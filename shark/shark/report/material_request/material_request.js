// Copyright (c) 2016, jyoti and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Material Request"] = {
	"filters": [

		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project"
		},
		{
			"fieldname": "bom_no",
			"label": __("BOM No"),
			"fieldtype": "Link",
			"options": "BOM"
		}

	],

};