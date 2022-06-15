# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from xml.etree.ElementTree import tostring
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from collections import defaultdict
from datetime import datetime
from datetime import date

sum_data = []
def execute(filters=None):
	global data
	columns = []
	data = []
	material_request = " "

	if filters.get("material_request"):
		material_request = filters.get("material_request")
		print("material_request",material_request)
		
	columns = get_columns()
	mr_details = fetching_mr_details(material_request)
	print("mr_details",mr_details)
	ordered_qty=0
	draft_qty=0		
	for mr_data in mr_details:
		supplier = frappe.db.sql("""select default_supplier from `tabItem Default` where parent='"""+mr_data['item_code']+"""'""", as_dict=1)
		print(supplier)
		ordered_qty=frappe.db.sql("""select sum(poi.qty) as ordered_qty from  `tabPurchase Order` po,`tabPurchase Order Item` poi 
		where po.name=poi.parent and po.docstatus=1 and 
		poi.item_code='"""+mr_data['item_code']+"""' and
		poi.material_request='"""+mr_data['name']+"""'""", as_dict=1)
		print("ordered_qty[0]['ordered_qty']",ordered_qty[0]['ordered_qty'])
		draft_qty=frappe.db.sql("""select sum(poi.qty) as draft_qty from  `tabPurchase Order` po,`tabPurchase Order Item` poi 
		where po.name=poi.parent and po.docstatus=0 and 
		poi.item_code='"""+mr_data['item_code']+"""' and
		poi.material_request='"""+mr_data['name']+"""'""", as_dict=1)
		print("draft_qty[0]['draft_qty']",draft_qty[0]['draft_qty'])
		if ordered_qty[0]['ordered_qty'] is None:
			ordered_qty=0
		else:
			ordered_qty=ordered_qty[0]['ordered_qty']	
		if draft_qty[0]['draft_qty'] is None:
			draft_qty=0
		else:
			draft_qty=draft_qty[0]['draft_qty']

		balance_qty=mr_data['qty']-(ordered_qty+draft_qty)
		data.append([mr_data['name'],mr_data['item_code'],
		mr_data['qty'],ordered_qty,draft_qty,balance_qty,
		mr_data['stock_uom'],supplier[0]['default_supplier'],
		])
		print("data",data)
	
	return columns,data



@frappe.whitelist()
def create_po(material_request):
	
	mr_details = fetching_mr_details(material_request)
	print("mr_details",mr_details)
	test_list=[]
	supplier_list=[]
	ordered_qty=0
	draft_qty=0	
	balance_qty=0		
	for mr_data in mr_details:
		supplier = frappe.db.sql("""select default_supplier from `tabItem Default` where parent='"""+mr_data['item_code']+"""'""", as_dict=1)
		print(supplier)
		supplier_list.append(supplier[0]['default_supplier'])
		
	test_list = list(set(supplier_list))
	print("test_list",test_list)
	filtered_list = list(filter(None, test_list))
	print("filtered_list",filtered_list)
	for supplier_details in filtered_list:
		items = frappe.db.sql("""select mr.name,mri.item_code,mri.qty,mri.schedule_date,mr.schedule_date as reqd_by_date,mri.stock_uom,id.default_supplier from `tabMaterial Request` as mr inner join 
	`tabMaterial Request Item` as mri on mr.name=mri.parent and 
	mr.name='"""+material_request+"""' inner join `tabItem Default` id on id.parent=mri.item_code 
	and id.default_supplier='"""+supplier_details+"""' """, as_dict=1)
		print("items",items)
		outerJson_po = {
		"doctype": "Purchase Order",
		"supplier": supplier_details,
		"schedule_date":items[0]['reqd_by_date'],
		"items": []
		}
		for items_details in items:
			ordered_qty=frappe.db.sql("""select sum(poi.qty) as ordered_qty from  `tabPurchase Order` po,`tabPurchase Order Item` poi 
		where po.name=poi.parent and po.docstatus=1 and 
		poi.item_code='"""+items_details['item_code']+"""' and
		poi.material_request='"""+material_request+"""'""", as_dict=1)
			print("ordered_qty[0]['ordered_qty']",ordered_qty[0]['ordered_qty'])
			draft_qty=frappe.db.sql("""select sum(poi.qty) as draft_qty from  `tabPurchase Order` po,`tabPurchase Order Item` poi 
			where po.name=poi.parent and po.docstatus=0 and 
			poi.item_code='"""+items_details['item_code']+"""' and
			poi.material_request='"""+material_request+"""'""", as_dict=1)
			print("draft_qty[0]['draft_qty']",draft_qty[0]['draft_qty'])
			if ordered_qty[0]['ordered_qty'] is None:
				ordered_qty=0
			else:
				ordered_qty=ordered_qty[0]['ordered_qty']	
			if draft_qty[0]['draft_qty'] is None:
				draft_qty=0
			else:
				draft_qty=draft_qty[0]['draft_qty']

			balance_qty=items_details['qty']-(ordered_qty+draft_qty)
			print("balance qty----",balance_qty)
			if balance_qty!=0:
				innerJson = {
			"item_code":items_details['item_code'],
			"qty":balance_qty,
			"stock_uom": items_details['stock_uom'],
			"material_request":material_request,
			"schedule_date":items_details['schedule_date'],
			"doctype": "Purchase Order Item"
			}
				outerJson_po['items'].append(innerJson)
		print("outerJson_po",outerJson_po)
		if outerJson_po['items']!=[]:
			doc_new_po = frappe.new_doc("Purchase Order")
			print("----------------------------")
			doc_new_po.update(outerJson_po)
			print("++++++++++++")
			doc_new_po.save()
			frappe.db.commit()
			print("=============================")
			frappe.msgprint("Po created succesfully")
		else:
			frappe.msgprint("Po Already created")

			

def fetching_mr_details(material_request):
	t_data = frappe.db.sql("""select mr.name,mri.item_code,mri.qty,mri.stock_uom from `tabMaterial Request` as mr inner join `tabMaterial Request Item` as mri where mr.name=mri.parent and mr.name='"""+material_request+"""'""", as_dict=1)

	return t_data

def get_columns():
	"""return columns"""
	columns = [
		_("Material Request No")+"::150",
		_("Item Code")+":Link/Item:200",
		_("Original Qty")+"::100",
		_("Ordered Qty")+"::100",
		_("Draft Po Qty")+"::100",
		_("Balance Qty")+"::100",
		_("Stock Uom")+"::100",
		_("Supplier")+"::150"
		]
	return columns