# Copyright (c) 2013, pavithra M R and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe import _, msgprint
from frappe.utils import flt, getdate, comma_and
from datetime import datetime, date
from collections import defaultdict
from datetime import datetime
from datetime import date
import time
import math
import json
import ast

sum_data = []
def execute(filters=None):
	global sum_data
	columns = []
	sum_data = []
	sales_order = ""
	sales_order = filters.get("sales_order")
	print("sales_order=============",sales_order)

	columns = get_columns()
	
	data = fetching_so_related_qad(sales_order)
	print("d",data)

	for gate_data in data:
		item_code=gate_data['item_code']
		sales_order_data = fetching_so_data(sales_order,item_code)
		print("sales_order_data",sales_order_data)
		if gate_data['sales_order']:
			sum_data.append([ gate_data['sales_order'],sales_order_data[0]['bom'],sales_order_data[0]		['customer'],sales_order_data[0]['pch_print_name'],
			sales_order_data[0]['project_format'],sales_order_data[0]['store_location'],
			sales_order_data[0]['item_code'],sales_order_data[0]['item_name'],sales_order_data[0]['qty'],gate_data['qc_passed'],
			gate_data['pending_qty_for_qc'],gate_data['qc_qty_cleared'],
			gate_data['balance_qty_for_qc'],gate_data['name'],gate_data['entry_date'].strftime("%d-%m-%Y")])
			print("111111",sum_data)
	return columns, sum_data

def fetching_so_related_qad(sales_order):
	gate_data = frappe.db.sql("""select qa.name,qa.entry_date,qa.sales_order,qai.item_code,qai.qty_in_so,qai.qc_passed,qai.pending_qty_for_qc,qai.qc_qty_cleared,qai.balance_qty_for_qc 
	from `tabQuality Assurance Document` as qa join `tabQuality Assurance Document Items` as qai on qa.name = qai.parent where qa.sales_order ='"""+sales_order+"""' order by qa.name""", as_dict=1)
	print("gate_data.....",gate_data)
	return gate_data

def fetching_so_data(sales_order,item_code):
	so_data = frappe.db.sql("""select so.name,so.bom,so.customer,so.pch_print_name,so.project_format,
	so.store_location,soi.item_code,soi.item_name,soi.qty 
	from `tabSales Order` as so join `tabSales Order Item` as soi on so.name = soi.parent 
	where so.name ='"""+sales_order+"""' and soi.item_code='"""+item_code+"""' """, as_dict=1)
	print("so_data.....",so_data)
	return so_data

def get_columns():
	"""return columns"""
	columns = [
			("Sales Order")+"::150",
			("Project No/BOM No")+"::150",
			("Customer")+"::150",
			("Print Name")+"::150",
			("Project Format")+"::150",
			("Store Location")+"::150",
			("Item Code")+":150",
			("Item Name")+":150",
			("Qty")+":150",
			("QC Passed")+"::150",
			("Pending Qty For QC")+":150",
			("Qc Qty Cleared")+":150",
			("Balance Qty for QC")+":150",
			("QAD Number")+":Link/Quality Assurance Document:150",
			("Entry Date")+"::150",
		]
	return columns
