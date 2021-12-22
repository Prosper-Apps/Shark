# Copyright (c) 2013, jyoti and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
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
    
    data_rate = []
    columns = get_columns()
    po_details = fetching_po_details(filters)
    for po_data in po_details:
	    ordered_qty = po_data["ordered_qty"]
	    delivered_qty = po_data["delivered_qty"]
	    pending_qty =ordered_qty - delivered_qty
	    actual_qty = po_data['qty']
	    item_code = po_data['item_code']
	    Shortage_Qty=actual_qty -pending_qty
	    if pending_qty > 0  and actual_qty>0:
	        data_rate.append(item_code)
	        if item_code   in data_rate and actual_qty > 0:
	            sum_data.append([ po_data['item_code'],po_data['item_name'], po_data['ordered_qty'],
	                po_data['delivered_qty'], pending_qty, po_data['warehouse'],actual_qty,Shortage_Qty,
	                po_data['stock_qty'], po_data['stock_uom'], po_data['supplier'],   po_data['rate']
	                ])
	    else:
	        if actual_qty==0:
	            if item_code  not in data_rate :
	                data_rate.append(item_code)
	                sum_data.append([ po_data['item_code'],po_data['item_name'], po_data['ordered_qty'],
	                    po_data['delivered_qty'], pending_qty,"",actual_qty,Shortage_Qty,
	                    po_data['stock_qty'], po_data['stock_uom'], po_data['supplier'],   po_data['rate']
	                    ])

    return columns, sum_data

@frappe.whitelist()
def fetch_so_list(master_customer):
	so_list = frappe.db.sql("""select tso.name 
	from `tabSales Order` tso,`tabCustomer` tc 
	where  tc.master_customer='"""+master_customer+"""' and tc.name=tso.customer""",
     as_dict=1)
	print("so_list",so_list)
	
	return so_list

def fetching_po_details(filters):
	condition = get_conditions(filters)
	po_data = frappe.db.sql("""select
					tso.name,tsoi.item_code,tsoi.qty as ordered_qty,tsoi.stock_uom as stock_uom, tsoi.delivered_qty,
					tsoi.warehouse as warehouse, tsoi.rate as rate,tsoi.supplier as supplier,tsoi.stock_qty,tb.warehouse,
										tb.actual_qty as qty,tsoi.item_name
			from
				`tabSales Order` tso,`tabSales Order Item` tsoi,`tabBin` tb
			where
				tso.name=tsoi.parent and tso.docstatus=1 and tsoi.item_code = tb.item_code and tso.name in %s""" % condition, as_dict=1)
	print("po_data",po_data)
	return po_data



def get_columns():
	"""return columns"""
	columns = [
		_("Item")+":Link/Item:100",
		_("Item Name")+"::100",
		_("Quantity")+":100",
		_("Delivered Quantity")+"::100",
		_("Pending Quantity")+"::100",
		_("Warehouse")+":Link/Warehouse:100",
		_("Available Qty")+"::100",
		_("Shortage/Excess Qty")+"::100",
		 ]
	return columns

def get_conditions(filters):
	conditions=""
	if filters.get("sales_order1"):
		conditions += '(%s)'  % frappe.db.escape(filters.get("sales_order1"), percent=False)
	if filters.get("sales_order2"):	
		conditions="("+"'"+filters.get("sales_order1")+"'"+","+'%s'")" % frappe.db.escape(filters.get("sales_order2"), percent=False)
	if filters.get("sales_order3"):
		conditions="("+"'"+filters.get("sales_order1")+"'"+","+"'"+filters.get("sales_order2")+"'"+","+'%s'")"  % frappe.db.escape(filters.get("sales_order3"), percent=False)
	if filters.get("sales_order4"):
		conditions="("+"'"+filters.get("sales_order1")+"'"+","+"'"+filters.get("sales_order2")+"'"+","+"'"+filters.get("sales_order3")+"'"+","+'%s'")"  % frappe.db.escape(filters.get("sales_order4"), percent=False)
	if filters.get("sales_order5"):
		conditions="("+"'"+filters.get("sales_order1")+"'"+","+"'"+filters.get("sales_order2")+"'"+","+"'"+filters.get("sales_order3")+"'"+","+"'"+filters.get("sales_order4")+"'"+","+'%s'")" % frappe.db.escape(filters.get("sales_order5"), percent=False)
	print("conditions",conditions)
	return conditions