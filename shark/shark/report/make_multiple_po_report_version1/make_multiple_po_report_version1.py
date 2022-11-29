# Copyright (c) 2013, pavithra M R and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from xml.etree.ElementTree import tostring
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from collections import defaultdict
from datetime import datetime
from datetime import date
import json 
sum_data = []
def execute(filters=None):
	global data
	columns = []
	data = []
	items_no_default=[]
	items_no_default_supplier=[]
	material_request = " "

	if filters.get("material_request"):
		material_request = filters.get("material_request")
		print("material_request",material_request)
		
	columns = get_columns()
	mr_details = fetching_mr_details(material_request)
	print("mr_details",mr_details)
	ordered_qty=0
	draft_qty=0
	not_supplier = filters.get("not_supplier")
	print("not_supplier",not_supplier)
	if not_supplier!=1:	
		for mr_data in mr_details:
			item_code=mr_data['item_code']
			supplier = frappe.db.sql("""select default_supplier from `tabItem Default` where parent=%(item_code)s""",{'item_code':item_code}, as_dict=1)
			print(supplier)
			ordered_qty=frappe.db.sql("""select sum(poi.qty) as ordered_qty from  `tabPurchase Order` po,`tabPurchase Order Item` poi 
			where po.name=poi.parent and po.docstatus=1 and 
			poi.item_code=%(item_code)s and
			poi.material_request='"""+mr_data['name']+"""'""",{'item_code':item_code}, as_dict=1)
			print("ordered_qty[0]['ordered_qty']",ordered_qty[0]['ordered_qty'])
			draft_qty=frappe.db.sql("""select sum(poi.qty) as draft_qty from  `tabPurchase Order` po,`tabPurchase Order Item` poi 
			where po.name=poi.parent and po.docstatus=0 and 
			poi.item_code=%(item_code)s and
			poi.material_request='"""+mr_data['name']+"""'""",{'item_code':item_code}, as_dict=1)
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
			data.append([mr_data['name'],mr_data['material_request_name'],mr_data['item_code'],mr_data['schedule_date'],
			mr_data['qty'],mr_data['warehouse'],mr_data['item_group'],ordered_qty,draft_qty,balance_qty,
			mr_data['stock_uom'],supplier[0]['default_supplier'],
			])
			print("data",data)
	
	if not_supplier==1:
		for mr_data in mr_details:
			item_code=mr_data['item_code']
			supplier = frappe.db.sql("""select default_supplier from `tabItem Default` where parent=%(item_code)s""",{'item_code':item_code}, as_dict=1)
			print(supplier)
			ordered_qty=frappe.db.sql("""select sum(poi.qty) as ordered_qty from  `tabPurchase Order` po,`tabPurchase Order Item` poi 
			where po.name=poi.parent and po.docstatus=1 and 
			poi.item_code=%(item_code)s and
			poi.material_request='"""+mr_data['name']+"""'""",{'item_code':item_code}, as_dict=1)
			print("ordered_qty[0]['ordered_qty']",ordered_qty[0]['ordered_qty'])
			draft_qty=frappe.db.sql("""select sum(poi.qty) as draft_qty from  `tabPurchase Order` po,`tabPurchase Order Item` poi 
			where po.name=poi.parent and po.docstatus=0 and 
			poi.item_code=%(item_code)s and
			poi.material_request='"""+mr_data['name']+"""'""",{'item_code':item_code}, as_dict=1)
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
			if supplier[0]['default_supplier'] is None:
				data.append([mr_data['name'],mr_data['material_request_name'],mr_data['item_code'],mr_data['schedule_date'],
			mr_data['qty'],mr_data['warehouse'],mr_data['item_group'],ordered_qty,draft_qty,balance_qty,
			mr_data['stock_uom'],supplier[0]['default_supplier'],
			])
			print("data======",data)
			
    	
	return columns,data,items_no_default


@frappe.whitelist()
def create_selected_row_po(checked_rows,supplier):
	#print("filters",type(filters))
	items=json.loads(checked_rows)
	print("items",items)
	outerJson_po = {
		"doctype": "Purchase Order",
		"supplier": supplier,
		"company":"Merit Systems",
		"material_request":items[0]['material_request_no'],
		"items": []
		}
	for items_details in items:
		print("items_details",items_details)
		item_code=items_details['item_code']
		ordered_qty=frappe.db.sql("""select sum(poi.qty) as ordered_qty from  `tabPurchase Order` po,`tabPurchase Order Item` poi 
		where po.name=poi.parent and po.docstatus=1 and 
		poi.item_code=%(item_code)s and
		poi.material_request='"""+items_details['material_request_no']+"""'""",{'item_code':item_code}, as_dict=1)
		print("ordered_qty[0]['ordered_qty']",ordered_qty[0]['ordered_qty'])
		draft_qty=frappe.db.sql("""select sum(poi.qty) as draft_qty from  `tabPurchase Order` po,`tabPurchase Order Item` poi 
		where po.name=poi.parent and po.docstatus=0 and 
		poi.item_code=%(item_code)s and
		poi.material_request='"""+items_details['material_request_no']+"""'""",{'item_code':item_code}, as_dict=1)
		print("draft_qty[0]['draft_qty']",draft_qty[0]['draft_qty'])
		if ordered_qty[0]['ordered_qty'] is None:
			ordered_qty=0
		else:
			ordered_qty=ordered_qty[0]['ordered_qty']	
		if draft_qty[0]['draft_qty'] is None:
			draft_qty=0
		else:
			draft_qty=draft_qty[0]['draft_qty']

		balance_qty=items_details['original_qty']-(ordered_qty+draft_qty)
		print("balance qty----",balance_qty)
		last_purchase_rate = frappe.db.sql("""select last_purchase_rate from `tabItem` where item_code=%(item_code)s""",{'item_code':item_code}, as_dict=1)
		print("last_purchase_rate",last_purchase_rate)		
		if balance_qty!=0:
			innerJson = {
		"item_code":items_details['item_code'],
		"material_request_item":items_details['material_request_name'],
		"qty":balance_qty,
		"rate":last_purchase_rate[0]['last_purchase_rate'],
		"stock_uom": items_details['stock_uom'],
		"warehouse":items_details['warehouse'],
		"material_request":items_details['material_request_no'],
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
		item_code=mr_data['item_code']
		supplier = frappe.db.sql("""select default_supplier from `tabItem Default` where parent=%(item_code)s""",{'item_code':item_code}, as_dict=1)
		print(supplier)
		supplier_list.append(supplier[0]['default_supplier'])
		
	test_list = list(set(supplier_list))
	print("test_list",test_list)
	filtered_list = list(filter(None, test_list))
	print("filtered_list",filtered_list)
	for supplier_details in filtered_list:
		items = frappe.db.sql("""select mr.name,mri.item_code,mri.name as material_request_name,mri.qty,mri.schedule_date,mri.warehouse,mr.schedule_date as reqd_by_date,mri.stock_uom,id.default_supplier from `tabMaterial Request` as mr inner join 
	`tabMaterial Request Item` as mri on mr.name=mri.parent and 
	mr.name='"""+material_request+"""' inner join `tabItem Default` id on id.parent=mri.item_code 
	and id.default_supplier='"""+supplier_details+"""' """, as_dict=1)
		print("items",items)
		outerJson_po = {
		"doctype": "Purchase Order",
		"supplier": supplier_details,
		"company":"Merit Systems",
		"schedule_date":items[0]['reqd_by_date'],
		"material_request":material_request,
		"items": []
		}
		for items_details in items:
			item_code=items_details['item_code']
			ordered_qty=frappe.db.sql("""select sum(poi.qty) as ordered_qty from  `tabPurchase Order` po,`tabPurchase Order Item` poi 
			where po.name=poi.parent and po.docstatus=1 and 
			poi.item_code=%(item_code)s and
			poi.material_request='"""+material_request+"""'""",{'item_code':item_code}, as_dict=1)
			print("ordered_qty[0]['ordered_qty']",ordered_qty[0]['ordered_qty'])
			draft_qty=frappe.db.sql("""select sum(poi.qty) as draft_qty from  `tabPurchase Order` po,`tabPurchase Order Item` poi 
			where po.name=poi.parent and po.docstatus=0 and 
			poi.item_code=%(item_code)s and
			poi.material_request='"""+material_request+"""'""",{'item_code':item_code}, as_dict=1)
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
			last_purchase_rate = frappe.db.sql("""select last_purchase_rate from `tabItem` where item_code=%(item_code)s""",{'item_code':item_code},as_dict=1)
			print("last_purchase_rate",last_purchase_rate)
			print("material_request_name.............",items_details['material_request_name'])
			if balance_qty!=0:
				innerJson = {
			"item_code":items_details['item_code'],
			"material_request_item":items_details['material_request_name'],
			"qty":balance_qty,
			"rate":last_purchase_rate[0]['last_purchase_rate'],
			"stock_uom": items_details['stock_uom'],
			"warehouse":items_details['warehouse'],
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
	t_data = frappe.db.sql("""select mr.name,mri.item_code,mri.name as material_request_name,mri.schedule_date,mri.qty,mri.stock_uom,mri.warehouse,mri.item_group from `tabMaterial Request` as mr inner join `tabMaterial Request Item` as mri where mr.name=mri.parent and mr.name='"""+material_request+"""'""", as_dict=1)

	return t_data

def get_columns():
	"""return columns"""
	columns = [
		_("Material Request No")+"::150",
		_("Material Request Name")+"::150",
		_("Item Code")+":Link/Item:200",
		_("Schedule Date")+"::200",
		_("Original Qty")+"::100",
		_("Warehouse")+"::200",
		_("Item Group")+"::200",
		_("Ordered Qty")+"::100",
		_("Draft Po Qty")+"::100",
		_("Balance Qty")+"::100",
		_("Stock Uom")+"::100",
		_("Supplier")+"::150"
		]
	return columns
