// Copyright (c) 2016, jyoti and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["FG Availability Against SO"] = {
	"filters": [{
        "fieldname": "company",
        "label": __("Company"),
        "fieldtype": "Link",
        "options": "Company",
        "reqd": 1
	},
	{
		"fieldname": "master_customer",
		"label": __("Master Customer"),
		"fieldtype": "Select",
		"reqd": 1,
		"options": ["Adidas", "Puma"],
		
	},
       {
        "fieldname": "sales_order1",
        "label": __("Sales Order1"),
        "fieldtype": "Link",
        "options": "Sales Order",
        "reqd": 1,
        "get_query": function() {
			var master_customer = frappe.query_report.get_filter_value("master_customer");
			var company = frappe.query_report.get_filter_value("company");
			console.log("company",company)
			if (company == null || company =="" || company == "undefined") {
				frappe.throw("Company should not be empty.Please select company first")
			}
			if (master_customer == null) {
				frappe.throw("Master Customer should not be empty.Please select master_customer first")
			}
			
			if (master_customer != null && company != null) {
			var list_customer=[]
			frappe.call({
				method: "shark.shark.report.fg_availability_against_so.fg_availability_against_so.fetch_so_list",
				args: {
						  "master_customer":master_customer
					},
				async: false,
				callback: function(r) 
					  { 
						for (var i = 0; i < r.message.length; i++) {
							list_customer.push(r.message[i].name);
							
						}
						
						console.log("list_customer",list_customer)
					  }
					})
					  
	           return {
                    "doctype": "Sales Order",
		     "filters" : [
			['Sales Order', 'docstatus', '!=', '2'],
			['Sales Order', 'name', 'IN', list_customer],
			['Sales Order', 'company', '=', company],
			]
			  }
			}
		 },
		 
},
{
	"fieldname": "sales_order2",
	"label": __("Sales Order2"),
	"fieldtype": "Link",
	"options": "Sales Order",
	"get_query": function() {
		var master_customer = frappe.query_report.get_filter_value("master_customer");
		var company = frappe.query_report.get_filter_value("company");
		console.log("company",company)
		if (company == null || company =="" || company == "undefined") {
			frappe.throw("Company should not be empty.Please select company first")
		}
		if (master_customer == null) {
			frappe.throw("Master Customer should not be empty.Please select master_customer first")
		}
		
		if (master_customer != null && company != null) {
		var list_customer=[]
		frappe.call({
			method: "shark.shark.report.fg_availability_against_so.fg_availability_against_so.fetch_so_list",
			args: {
					  "master_customer":master_customer
				},
			async: false,
			callback: function(r) 
				  { 
					for (var i = 0; i < r.message.length; i++) {
						list_customer.push(r.message[i].name);
						
					}
					
					console.log("list_customer",list_customer)
				  }
				})
				  
		   return {
				"doctype": "Sales Order",
		 "filters" : [
		['Sales Order', 'docstatus', '!=', '2'],
		['Sales Order', 'name', 'IN', list_customer],
		]
		  }
		}
	 },
	 
},
{
	"fieldname": "sales_order3",
	"label": __("Sales Order3"),
	"fieldtype": "Link",
	"options": "Sales Order",
	"get_query": function() {
		var master_customer = frappe.query_report.get_filter_value("master_customer");
		var company = frappe.query_report.get_filter_value("company");
		console.log("company",company)
		if (company == null || company =="" || company == "undefined") {
			frappe.throw("Company should not be empty.Please select company first")
		}
		if (master_customer == null) {
			frappe.throw("Master Customer should not be empty.Please select master_customer first")
		}
		
		if (master_customer != null && company != null) {
		var list_customer=[]
		frappe.call({
			method: "shark.shark.report.fg_availability_against_so.fg_availability_against_so.fetch_so_list",
			args: {
					  "master_customer":master_customer
				},
			async: false,
			callback: function(r) 
				  { 
					for (var i = 0; i < r.message.length; i++) {
						list_customer.push(r.message[i].name);
						
					}
					
					console.log("list_customer",list_customer)
				  }
				})
				  
		   return {
				"doctype": "Sales Order",
		 "filters" : [
		['Sales Order', 'docstatus', '!=', '2'],
		['Sales Order', 'name', 'IN', list_customer],
		]
		  }
		}
	 },
	 
},
{
	"fieldname": "sales_order4",
	"label": __("Sales Order4"),
	"fieldtype": "Link",
	"options": "Sales Order",
	"get_query": function() {
		var master_customer = frappe.query_report.get_filter_value("master_customer");
		var company = frappe.query_report.get_filter_value("company");
		console.log("company",company)
		if (company == null || company =="" || company == "undefined") {
			frappe.throw("Company should not be empty.Please select company first")
		}
		if (master_customer == null) {
			frappe.throw("Master Customer should not be empty.Please select master_customer first")
		}
		
		if (master_customer != null && company != null) {
		var list_customer=[]
		frappe.call({
			method: "shark.shark.report.fg_availability_against_so.fg_availability_against_so.fetch_so_list",
			args: {
					  "master_customer":master_customer
				},
			async: false,
			callback: function(r) 
				  { 
					for (var i = 0; i < r.message.length; i++) {
						list_customer.push(r.message[i].name);
						
					}
					
					console.log("list_customer",list_customer)
				  }
				})
				  
		   return {
				"doctype": "Sales Order",
		 "filters" : [
		['Sales Order', 'docstatus', '!=', '2'],
		['Sales Order', 'name', 'IN', list_customer],
		]
		  }
		}
	 },
	 
},
{
	"fieldname": "sales_order5",
	"label": __("Sales Order5"),
	"fieldtype": "Link",
	"options": "Sales Order",
	"get_query": function() {
		var master_customer = frappe.query_report.get_filter_value("master_customer");
		var company = frappe.query_report.get_filter_value("company");
		console.log("company",company)
		if (company == null || company =="" || company == "undefined") {
			frappe.throw("Company should not be empty.Please select company first")
		}
		if (master_customer == null) {
			frappe.throw("Master Customer should not be empty.Please select master_customer first")
		}
		
		if (master_customer != null && company != null) {
		var list_customer=[]
		frappe.call({
			method: "shark.shark.report.fg_availability_against_so.fg_availability_against_so.fetch_so_list",
			args: {
					  "master_customer":master_customer
				},
			async: false,
			callback: function(r) 
				  { 
					for (var i = 0; i < r.message.length; i++) {
						list_customer.push(r.message[i].name);
						
					}
					
					console.log("list_customer",list_customer)
				  }
				})
				  
		   return {
				"doctype": "Sales Order",
		 "filters" : [
		['Sales Order', 'docstatus', '!=', '2'],
		['Sales Order', 'name', 'IN', list_customer],
		]
		  }
		}
	 },
	 
}
]
}