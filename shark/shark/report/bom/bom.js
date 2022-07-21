// Copyright (c) 2016, jyoti and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["BOM"] = {
	"filters": [{
		"fieldname": "company",
		"label": __("Company"),
		"fieldtype": "Link",
		"options": "Company",
		"reqd": 1
	},
{
		"fieldname": "project",
		"label": __("Project"),
		"fieldtype": "Link",
		"options": "Project",
	"reqd": 1,
	"get_query": function(){
	return {
		"doctype": "Project",
		"filters": {
			"is_active": "Yes"
		}
	}
	},
	"on_change": function(query_report) {
		 var project = frappe.query_report.get_filter_value("project");
	console.log("project-------"+project);
	frappe.call({
		method: "shark.shark.report.bom.bom.fetch_project_details",
		args: {
				  "project":project
			},
		async: false,
		callback: function(r) 
			  { 
			if(r.message){
			console.log("docids options::"+r.message.length);
			console.log("message::"+JSON.stringify(r.message));

			var project_warehouse = r.message[0].project_warehouse;
			var reserve_warehouse = r.message[0].reserve_warehouse;
			var master_bom = r.message[0].master_bom;
			var core_team_coordinator = r.message[0].core_team_coordinator;
			var planner = r.message[0].planner;
			var start_date = r.message[0].start_date;

			if (project_warehouse != null) {
			console.log("project_warehouse::"+ project_warehouse);
			frappe.query_report.set_filter_value("warehouse", "");
			frappe.query_report.set_filter_value("warehouse", project_warehouse);
			frappe.query_report.refresh();
			}else{
			frappe.query_report.set_filter_value("warehouse", "");
			frappe.query_report.refresh();
			}
			
			if (reserve_warehouse != null) {
			console.log("reserve_warehouse::"+ reserve_warehouse);
			frappe.query_report.set_filter_value("reserve_warehouse", "");
			frappe.query_report.set_filter_value("reserve_warehouse", reserve_warehouse);
			frappe.query_report.refresh();
			}else{
			frappe.query_report.set_filter_value("reserve_warehouse", "");
			frappe.query_report.refresh();
			}

			if (master_bom != null) {
			console.log("master_bom::"+ master_bom);
			frappe.query_report.set_filter_value("bom", "");
			frappe.query_report.set_filter_value("bom", master_bom);
			var qty = frappe.query_report.get_filter_value("qty_to_make");
				var check_for_whole_number_flag = check_for_whole_number(master_bom, qty, query_report);
				if (check_for_whole_number_flag) {
						frappe.msgprint(__("Quantity to Make should be whole number"));
			}
			frappe.query_report.refresh();
			}else{
			frappe.query_report.set_filter_value("bom", "");
			frappe.query_report.refresh();
			}
			
			if (core_team_coordinator != null) {
			frappe.query_report.set_filter_value("core_team_coordinator", "");
			frappe.query_report.set_filter_value("core_team_coordinator", core_team_coordinator);
			
			frappe.query_report.refresh();
			}else{
			console.log("core_team_coordinator::"+ core_team_coordinator);
			frappe.query_report.set_filter_value("core_team_coordinator", "null");
			
			frappe.query_report.refresh();
			}
			
			if (planner != null) {
			frappe.query_report.set_filter_value("planner", "");
			frappe.query_report.set_filter_value("planner", planner);
			
			frappe.query_report.refresh();
			}else{
			console.log("planner::"+ planner);
			frappe.query_report.set_filter_value("planner", "null");
			frappe.query_report.refresh();
			}
			
			if (start_date != null) {
			frappe.query_report.set_filter_value("start_date", "");
			frappe.query_report.set_filter_value("start_date", start_date);
			frappe.query_report.refresh();
			}else{
			frappe.query_report.set_filter_value("start_date", "");
			frappe.query_report.refresh();
			}
			}//end of if..
		}//end of call-back function..
	});//end of frappe call..
	}//end of on_change
	},
{
		"fieldname": "include_exploded_items",
		"label": __("Include Exploded Items"),
		"fieldtype": "Data",
	"options": "",
	"default": "Y",
	"hidden": 1
	},
{
		"fieldname": "qty_to_make",
		"label": __("Quantity To Make"),
		"fieldtype": "Data",
		"default": "1",
		"reqd": 1,
		"hidden": 1,
	"on_change": function(query_report) {
	var qty = frappe.query_report.get_filter_value("qty_to_make");
	var bom = frappe.query_report.get_filter_value("bom");

	if (!jQuery.isNumeric(qty)) {
				frappe.query_report.set_filter_value("qty_to_make", "1");
				frappe.throw("Quantity to Make value is not in proper format")
			}
			if (qty < 0) {
				frappe.query_report.set_filter_value("qty_to_make", "1");
				frappe.throw("Quantity to Make cannot be nagative please input positive value")
			}
			if (qty < 1) {
				frappe.query_report.set_filter_value("qty_to_make", "1");
				frappe.throw(" Quantity to Make should be greater than Zero")
			}
	if (bom!=null){
		var check_for_whole_number_flag = check_for_whole_number(bom, qty, query_report);
		if (check_for_whole_number_flag) {
					frappe.msgprint(__("Quantity to Make should be whole number"));
				}
	}
	query_report.refresh();
	}
},
{
		"fieldname": "bom",
		"label": __("BOM"),
		"fieldtype": "Link",
		"options": "BOM",
		"read_only":1
	},
{
		"fieldname": "warehouse",
		"label": __("Warehouse"),
		"fieldtype": "Data",
	"read_only": 1,
	"hidden": 1
	},
{
		"fieldname": "reserve_warehouse",
		"label": __("Reserve Warehouse"),
		"fieldtype": "Data",
	"read_only": 1,
	"hidden": 1
	},
{
		"fieldname": "core_team_coordinator",
		"label": __("Core Team Coordinator"),
		"fieldtype": "Data",
	"read_only": 1,
	"hidden": 1
	},
{
		"fieldname": "planner",
		"label": __("Planner"),
		"fieldtype": "Data",
	"read_only": 1,
	"hidden": 1
	},
{
		"fieldname": "start_date",
		"label": __("Start Date"),
		"fieldtype": "Data",
	"read_only": 1,
	"hidden": 1
	}
],

isNumeric: function(obj) {
	return !jQuery.isArray(obj) && (obj - parseFloat(obj) + 1) >= 0;
	},

}//end of report..




function check_for_whole_number(bomNO, qty, query_report) {
var check_for_whole_number = false;
frappe.call({
	method: "shark.shark.report.bom.bom.check_for_whole_number",
	args: {
		"bomno": bomNO
	},
	async: false,
	callback: function(r) {
		if (r.message && qty % 1 != 0) {
			check_for_whole_number = true;
			frappe.query_report.set_filter_value("qty_to_make", "1");
			frappe.query_report.refresh();
		} else {
			check_for_whole_number = false;
			frappe.query_report.refresh();
		}
	} //end of callback fun..
}) //end of frappe call..
return check_for_whole_number;
}