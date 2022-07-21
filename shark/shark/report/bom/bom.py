# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from erpnext.stock.stock_balance import get_balance_qty_from_sle
import datetime
import time
import math
import json
import ast


def execute(filters=None):
	global summ_data
	global company
	summ_data = []
	bom_items = []
	whse_items = []
	whse_qty = 0
	bom_qty = 0
	reserved_whse_qty = 0
	sum_qty = 0
	delta1_qty = 0
	whse_stock_entry_qty = 0
	reserved_whse_stock_entry_qty = 0
	company = filters.get("company")
	bom = filters.get("bom")
	quantity_to_make = filters.get("qty_to_make")
	include_exploded_items = filters.get("include_exploded_items")
	warehouse = filters.get("warehouse")
	reserve_warehouse = filters.get("reserve_warehouse")
	project_start_date = filters.get("start_date")
	columns = get_columns()
	data=[]
	if warehouse is not None:
		#print "warehouse-----------", warehouse
		whse_items = get_items_from_warehouse(warehouse)
		if whse_items is None:
			whse_items = []
		#print "whse_items-----------", whse_items
	if bom is not None:
		bom_items = get_bom_items(filters)
		if bom_items is None:
			bom_items = []
		#print "bom_items-----------", bom_items

	items_data = merger_items_list(whse_items,bom_items)
	#print "items_data-----------", items_data

	for item in sorted(items_data):
		dict_items = items_data[item]
		item_code = str(dict_items.item_code)
		bom_qty = dict_items.bom_qty
		bom_item_qty = dict_items.bi_qty
		
		if bom_qty!=0:
			required_qty = (bom_item_qty/bom_qty) * (float(quantity_to_make))
		else:
			required_qty = 0
		if warehouse is not None and warehouse !="":
			whse_qty = get_warehouse_qty(warehouse,item_code)
			whse_stock_entry_qty = get_stock_entry_quantities(warehouse,item_code,project_start_date)
		else:
			whse_qty = 0
			whse_stock_entry_qty = 0

		if whse_stock_entry_qty:
			whse_qty = whse_qty + whse_stock_entry_qty
		if reserve_warehouse is not None and reserve_warehouse!="":
			reserved_whse_qty = get_warehouse_qty(reserve_warehouse,item_code)
			reserved_whse_stock_entry_qty = get_stock_entry_quantities(reserve_warehouse,item_code,project_start_date)
		else:
			reserved_whse_qty = 0
			reserved_whse_stock_entry_qty = 0

		if reserved_whse_stock_entry_qty:
			reserved_whse_qty = reserved_whse_qty + reserved_whse_stock_entry_qty

		#delta_qty = whse_qty - bom_qty 
		delta_qty = whse_qty - required_qty
		sum_qty = whse_qty + reserved_whse_qty
		#delta1_qty = sum_qty - bom_qty
		delta1_qty = sum_qty - required_qty
		item_group=get_item_group(item_code)
		stock_uom=get_stock_uom(item_code)
		last_purchase_rate=get_last_purchase_rate(item_code)
		summ_data.append([str(),str(item_group),str(item_code),str(stock_uom),
		 			str(bom_item_qty),str(whse_qty),str(required_qty),str(reserved_whse_qty), 
					 str(sum_qty),str(),str(),
					str(last_purchase_rate),str(last_purchase_rate*required_qty),
					str(last_purchase_rate*sum_qty)])
		data=Sort(summ_data)
	print ("summ_data-----------", summ_data)
	return columns, data

def Sort(summ_data):
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of 
    # sublist lambda has been used
    summ_data.sort(key = lambda x: x[1])
    return summ_data

def get_item_group(item_code):
    item_group = frappe.db.sql("""select item_group from `tabItem` where item_code=%s""",(item_code), as_dict=1)
    return item_group[0]['item_group']

def get_stock_uom(item_code):
    stock_uom = frappe.db.sql("""select stock_uom from `tabItem` where item_code=%s""",(item_code), as_dict=1)
    return stock_uom[0]['stock_uom']

def get_last_purchase_rate(item_code):
    last_purchase_rate = frappe.db.sql("""select last_purchase_rate from `tabItem` where item_code=%s""",(item_code), as_dict=1)
    return last_purchase_rate[0]['last_purchase_rate']

def get_stock_entry_quantities(warehouse,item_code,project_start_date):
	total_qty = 0
	current_date = str(datetime.datetime.now())
	details = frappe.db.sql("""select sed.item_code,sed.qty,se.purpose from  `tabStock Entry Detail` sed, `tabStock Entry` se where 		  sed.item_code=%s and sed.s_warehouse=%s and se.purpose='Manufacture' and sed.modified >='""" + str(project_start_date) +"""'
		  and sed.modified <='""" + current_date + """' and sed.parent=se.name and se.docstatus=1""", (item_code,warehouse), as_dict=1)
	if len(details)!=0:
		#print "details------------", details
		for se_qty in details:
			if se_qty['qty'] is None:
				qty = 0
			else:
				qty = float(se_qty['qty'])
			total_qty = total_qty + qty
	return total_qty

def merger_items_list(whse_items,bom_items):
	items_map = {}
	if bom_items:
		for data in bom_items:
			item_code = data['item_code']
			bi_qty = data['bi_qty']
			bo_qty = data['bo_qty']
			#print "bom_item_qty--------", bi_qty
			key = (item_code)
			if key not in items_map:
				items_map[key] = frappe._dict({"item_code": item_code,"bi_qty": float(bi_qty),"bom_qty": bo_qty})
	if whse_items:
		for whse_items_data in 	whse_items:
			whse_item = whse_items_data['item_code']
			if whse_item not in items_map:
				key = whse_item
				items_map[key] = frappe._dict({"item_code": whse_item,"bi_qty": 0.0,"bom_qty": 0.0})
	return items_map

def get_warehouse_qty(warehouse,item_code):
	whse_qty = 0
	details = frappe.db.sql("""select actual_qty from `tabBin` where warehouse=%s and item_code=%s and actual_qty > 0 """,(warehouse,item_code), as_dict=1)
	if len(details)!=0:
		if details[0]['actual_qty'] is not None:
			whse_qty = details[0]['actual_qty']
	return whse_qty

def get_bom_qty(bom,item_code):
	bom_qty = 0
	details = frappe.db.sql("""select qty from `tabBOM Item` where parent=%s and item_code=%s""", (bom,item_code), as_dict=1)
	if len(details)!=0:
		if details[0]['qty'] is not None:
			bom_qty = details[0]['qty']
	return bom_qty

def get_items_from_warehouse(warehouse):
	whse_items = frappe.db.sql("""select item_code,actual_qty from `tabBin` where warehouse = %s and actual_qty > 0 group by item_code""", 					warehouse, as_dict=1)
	if len(whse_items)==0:
		whse_items = None
	return whse_items

def get_bom_items(filters):
	conditions = get_conditions(filters)
	#print "---------conditions::", conditions
	if filters.get("include_exploded_items") == "Y":
		#print "in------------Y"
		return frappe.db.sql("""select bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as bo_qty, bo.project, bi.item_code, bi.stock_qty as bi_qty from `tabBOM` bo, `tabBOM Explosion Item` bi where bo.name = bi.parent and bo.is_active=1 and bo.docstatus = "1" %s order by bo.name, bi.item_code""" % conditions, as_dict=1)
	else:
		return frappe.db.sql("""select bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as bo_qty, bo.project, bi.item_code, bi.stock_qty as bi_qty from `tabBOM` bo, `tabBOM Item` bi where bo.name = bi.parent and bo.is_active=1 and bo.docstatus = "1" %s order by bo.name, bi.item_code""" % conditions, as_dict=1)

def get_conditions(filters):
	conditions = ""
	if filters.get("company"):
		conditions += 'and bo.company = %s' % frappe.db.escape(filters.get("company"), percent=False)

	if filters.get("bom"):
		conditions += 'and bi.parent = %s' % frappe.db.escape(filters.get("bom"), percent=False)
	return conditions

@frappe.whitelist()
def fetch_project_details(project):
	details = frappe.db.sql("""select start_date,project_warehouse,reserve_warehouse,master_bom,core_team_coordinator,planner from 	`tabProject` where name=%s""", project, as_dict=1)
	return details


	
def get_columns():
	"""return columns"""
	columns = [
		_("PO NO")+"::100",
		_("Item Group")+":Link/Item Group:100",
		_("Item Code")+":Link/BOM:100",
		_("Stock UOM")+":Link/UOM:100",
		_("BOM Item Qty")+"::100",
		_("Qty issued for Production")+"::140",
		_("Required Qty")+"::100",
		_("Stock Qty")+"::150",
		_("Ordered Qty")+"::100",
		_("Planning Remark")+"::100",
		_("Store Remark")+"::100",
		_("Price/unit")+"::100",
		_("Total BOM cost")+"::100",
		_("Order Cost")+"::100"
		 ]
	return columns

@frappe.whitelist()
def check_for_whole_number(bomno):
	return (frappe.db.sql("""select must_be_whole_number from `tabUOM` where name IN (select uom from `tabBOM` where name = %s) """,(bomno)))

