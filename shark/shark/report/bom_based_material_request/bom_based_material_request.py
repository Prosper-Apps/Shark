# Copyright (c) 2013, jyoti and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from collections import defaultdict
import datetime
import json

def execute(filters=None):
	columns, data = [], []
	columns = get_columns()
	item_details=fetching_container_details(filters)
	print("item_details",item_details)
	for items in item_details:
		data.append(["",items['item_group'],items['item_code'],items['stock_uom'],items['qty_consumed_per_unit'],
		items['stock_qty'],items['qty_consumed_per_unit']-items['stock_qty'],"","",items['rate'],items['rate']*items['qty_consumed_per_unit'],
		items['rate']*(items['qty_consumed_per_unit']-items['stock_qty'])])
	#print("data",data)
	return columns, data

def fetching_container_details(filters):
	condition = get_conditions(filters)
	items = frappe.db.sql("""SELECT tbei.item_code,tbei.stock_qty,tbei.stock_uom,ti.item_code,ti.item_group,tbei.rate,tbei.qty_consumed_per_unit FROM `tabBOM Explosion Item` tbei JOIN `tabBOM` tb   
	ON tb.name=tbei.parent JOIN `tabItem` ti  
	ON  ti.item_code= tbei.item_code  %s order by ti.item_group """ % condition, as_dict=1)
	
	return items

def get_columns():
	"""return columns"""
	columns = [
			_("PO No.")+"::100",
			_("Item Group")+"::100",
			_("Item Code")+"::100",
			_("Stock Uom")+"::100",
			_("Total Qty")+"::100",
			_("Stock Qty")+":Link/Item:100",
			_("Order Qty")+"::100",
			_("Planning Remark")+"::100",
			_("Store Remark")+"::100",
			_("Price/unit")+"::100",
			_("Total BOM cost")+"::100",
			_("Order Cost")+"::100"
			

			]
	return columns

def get_conditions(filters):
	conditions=""
	
	if filters.get("bom_no"):
		conditions +='and tb.name = %s' % frappe.db.escape(filters.get("bom_no"), percent=False)

	print("condition",conditions)
	return conditions

