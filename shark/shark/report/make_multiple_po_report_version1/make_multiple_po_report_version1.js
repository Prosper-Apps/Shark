// Copyright (c) 2016, pavithra M R and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Make Multiple PO Report Version1"] = {
	"filters": [{
		"fieldname":"material_request",
		"label":__("Material Request"),
		"fieldtype":"Link",
		"options":"Material Request",
		"get_query": function() {
			return {
			"doctype": "Material Request",
			"filters": {
			"docstatus": 1,
			"material_request_type":"Purchase"
			}
			}
			}
},
{
	"fieldname": "not_supplier",
	"label": __("Items Not having default Supplier"),
	"fieldtype": "Check"
},
],
	onload: function(report) {

		let doc = frappe.query_report.report_name
		report.page.add_inner_button(__("Make PO for Default Supplier"), function() {
			console.log("doc",doc);
			var material_request = frappe.query_report.get_filter_value('material_request') ? frappe.query_report.get_filter_value('material_request') : ''
			console.log("material_request",material_request);
			create_po(material_request)
			frappe.set_route("List/Purchase Order/")
			})

		report.page.add_inner_button(__("Make PO for Non Default Supplier"), function() {
			// console.log(frappe.query_report.get_filter_value("show_dispatch_items"))
			var material_request = frappe.query_report.get_filter_value('material_request') ? frappe.query_report.get_filter_value('material_request') : ''
	console.log("material_request",material_request);
	var not_supplier = frappe.query_report.get_filter_value('not_supplier') ? frappe.query_report.get_filter_value('not_supplier') : ''
	console.log("not_supplier",not_supplier);
	let checked_rows_indexes = report.datatable.rowmanager.getCheckedRows();
            let checked_rows = checked_rows_indexes.map(i => report.data[i]);
			console.log("checked_rows", checked_rows)
			
			
			var d = new frappe.ui.Dialog({
				title: __("Select Supplier"),
				'fields': [
					{
						"fieldname": "supplier",
						"label": __("Supplier"),
						"fieldtype": "Link",
						"options": "Supplier",
        				"reqd": 1,
					},
					
				],
				primary_action: function(values){
					d.hide()
					var supplier = values.supplier
					console.log("supplier",supplier)
					var doc_name = get_rows_data(checked_rows,supplier)
					frappe.set_route("List/Purchase Order/")
				}
			});
			
			d.show()
		});
	
	},get_datatable_options(options) {
		return Object.assign(options, {
			checkboxColumn: true
		});
	},

};

function create_po(material_request) {
    frappe.call({
        method: 'aepl.aepl.report.make_multiple_po_report.make_multiple_po_report.create_po',
        args:{
			material_request:material_request
		},
        async: false,
        callback: function(r) {
            console.log("updated")

        }
    });
}

function get_rows_data(checked_rows,supplier) {
    console.log("---------------")
    frappe.call({
        method: 'aepl.aepl.report.make_multiple_po_report.make_multiple_po_report.create_selected_row_po',
		args: {
			checked_rows: checked_rows,
			supplier:supplier
		},
        async: false,
        callback: function(r) {
            console.log("updated")

        }
    });
}