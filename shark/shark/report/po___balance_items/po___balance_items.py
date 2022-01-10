# Copyright (c) 2013, Epoch and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from __future__ import division
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from collections import defaultdict
from datetime import datetime
import time
import math
import json
import ast
import sys


sum_data = []
def execute(filters=None):
	global sum_data
	columns = []
	sum_data = []
	global data
	global condition
	
	columns = get_columns()
	
	purchase_order_details = fetching_po_details(filters)
	for po_list_data in purchase_order_details:
		sum_data.append([po_list_data.date.strftime("%d-%m-%Y"),
		po_list_data.name,po_list_data.supplier,
		po_list_data.project,po_list_data.item_code,
		po_list_data.stock_uom,
		po_list_data.quantity,po_list_data.received_qty,
		(po_list_data.quantity-po_list_data.received_qty),po_list_data.status])
	#print("sum_data",sum_data)
	return columns, sum_data

def fetching_po_details(filters):
	condition = get_conditions(filters)
	po_data = frappe.db.sql("""select po.name,po.transaction_date as date,
	po.supplier,poi.project,poi.item_group,poi.stock_qty as quantity,
	poi.item_code,po.status,poi.stock_uom
	from 
	`tabPurchase Order` po,`tabPurchase Order Item` poi 
	where po.name=poi.parent and po.docstatus!=2 
	%s """ %
		condition, as_dict=1)
	#print("po_data",po_data)
	for data in po_data:
		#print("data.name",data)
		test_qty=frappe.db.sql("""select sum(received_stock_qty) as received_qty from `tabPurchase Receipt Item` 
		where purchase_order='"""+data.name+"""' group by item_code""", as_dict=1)
		#print("test_qty",test_qty)
		if len(test_qty)==0:
			data["received_qty"]=0

		elif (len(test_qty)!=0) and (test_qty[0].received_qty is not None):
			#print("enterd in if")
			data["received_qty"]=test_qty[0].received_qty
			
		else:
			#print("enterd in else")
			data["received_qty"]=0
			
	#print("po_data after",po_data)
	return po_data

def get_columns():
	"""return columns"""
	columns = [
			_("Date")+"::80",
			_("Name")+"::130",
			_("Supplier")+":Link/Supplier:150",
			_("Project")+":Link/Project:150",
			_("Item Code")+":Link/Item:200",
			_("UOM")+":Link/UOM:100",
			_("Quantity")+"::80",
			_("Received Qty")+"::100",
			_("Balance Qty")+"::100",
			_("Status")+"::100"
			]
	return columns

def get_conditions(filters):
	conditions=""
	if filters.get("from_date"):
		conditions += 'and po.transaction_date >= %s'  % frappe.db.escape(filters.get("from_date"), percent=False)
	if filters.get("to_date"):
		conditions +='and po.transaction_date <= %s' % frappe.db.escape(filters.get("to_date"), percent=False)
	if filters.get("status"):
		conditions += 'and po.status = %s'  % frappe.db.escape(filters.get("status"), percent=False)
	if filters.get("purchase_order"):
		conditions +='and po.name = %s' % frappe.db.escape(filters.get("purchase_order"), percent=False)
	if filters.get("supplier"):
		conditions += 'and po.supplier = %s'  % frappe.db.escape(filters.get("supplier"), percent=False)
	if filters.get("item_group"):
		conditions +='and poi.item_group = %s' % frappe.db.escape(filters.get("item_group"), percent=False)
	if filters.get("item_code"):
		conditions += 'and poi.item_code = %s'  % frappe.db.escape(filters.get("item_code"), percent=False)
	return conditions

