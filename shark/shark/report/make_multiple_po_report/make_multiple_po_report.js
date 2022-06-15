// Copyright (c) 2016, jyoti and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Make Multiple PO Report"] = {
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
],

onload: function(report) {
	let doc = frappe.query_report.report_name
	report.page.add_inner_button(__("Make PO"), function() {
	console.log("doc",doc);
	var material_request = frappe.query_report.get_filter_value('material_request') ? frappe.query_report.get_filter_value('material_request') : ''
	console.log("material_request",material_request);
	create_po(material_request)
	frappe.set_route("List/Purchase Order/")
	})
},get_datatable_options(options) {
	return Object.assign(options, {
		checkboxColumn: true
	});
},
};
function create_po(material_request) {
    frappe.call({
        method: 'shark.shark.report.make_multiple_po_report.make_multiple_po_report.create_po',
        args:{
			material_request:material_request
		},
        async: false,
        callback: function(r) {
            console.log("updated")

        }
    });
}