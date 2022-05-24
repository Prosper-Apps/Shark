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

def execute(filters=None):
	columns, data = [], []
	
	global bom
	item_name=""
	#print "report add total row-----------",report.add_total_row
	bom = ""
	company = filters.get("company")
	default_bom_available = ""
	sales_order = filters.get("sales_order")
	warehouse = filters.get("warehouse")
	print("warehouse",warehouse)
	columns = get_columns()
	input_cost_for_raw_material=""
	total_item_cost=0
	sales_item = sales_item_details(company ,sales_order)
	print("sales_item",sales_item)
	for items in sales_item:
		sales_item_code=items.item_code
		print("=========",sales_item_code)
		qty=items.qty
		print("=========",qty)
		stock_uom=items.stock_uom
		print("=========",stock_uom)
		bom=frappe.db.get_value("BOM",{"item":sales_item_code,"is_default":1},"name")
		print("item_default_bom",bom)
		if bom is None:
			default_bom_available="No"
			data.append([default_bom_available,bom,sales_item_code,
			"","","","",stock_uom,"","","","","","","","",""])
		#frappe.msgprint(" Item "+sales_item_code+" does not have default BOM")
		if bom is not None:
			bom_item = bom_details(company ,bom)
			default_bom_available="Yes"
			for bom_i in bom_item:
				bom_name = bom_i.bom_name
				bom_item = bom_i.bo_item
				bo_qty = bom_i.bo_qty
				item_code = bom_i.bi_item
				item_name = bom_i.item_name
				description = bom_i.description
				stock_uom = bom_i.stock_uom
				stock_qty = bom_i.bi_qty
				stock_ledger_entry = get_stock_ledger_entry(item_code)
				item_details = get_item_details(item_code)
				actual_stock_qty=warehouse_qty_details(item_code,warehouse)
				print("actual_stock_qty",actual_stock_qty)
				if len(actual_stock_qty) == 0:
					actual_qty=0.0
				else:
					actual_qty=actual_stock_qty[0]['actual_qty']
				pending_po_qty=fetch_po_details(item_code,warehouse)
				stock_valuation_price = 0.0
				last_purchase_rate = 0.0
				for code in item_details:
					purchase_uom = code.purchase_uom
					valuation_rate = code.valuation_rate
					item_group = code.item_group
					last_purchase = code.last_purchase_rate
					purchase_rate = get_sales_order_no(item_code)
					for stock in stock_ledger_entry:
						if stock.valuation_rate is not None:
							stock_valuation_price = stock.valuation_rate
					if last_purchase > 0:
						if code.last_purchase_rate is not None:
							last_purchase_rate = code.last_purchase_rate
							#print "last_purchase_rate-----------",last_purchase_rate
							check_last_purchase_rate = "Y"
							if stock_valuation_price == 0.0:
								stock_valuation_price = code.last_purchase_rate
								#print "stock_valuation_price====lpp=========",stock_valuation_price
					elif stock_valuation_price != 0.0:
						last_purchase_rate = stock_valuation_price
						check_last_purchase_rate = "N"
						#print "last_purchase_rate====svp=========",last_purchase_rate
					else:
						last_purchase_rate = valuation_rate
						#print "last_purchase_rate----vp-------",last_purchase_rate
						check_last_purchase_rate = "N"
						if stock_valuation_price == 0.0:
							stock_valuation_price = valuation_rate
							#print "stock_valuation_price====vp=========",stock_valuation_price
			
					if purchase_uom is not None:
						items_conversion = get_conversion_factore(item_code, purchase_uom)
						if items_conversion is not None:
							for conversion in items_conversion:
								conversion_factor = conversion.conversion_factor
					else:
						items_conversion = get_conversion_factore(item_code, stock_uom)
						if items_conversion is not None:
							for conversion in items_conversion:
								conversion_factor = conversion.conversion_factor
								conversion_factor = round(float(conversion_factor),2)
					valuation_cost_in_stock_uom=conversion_factor*last_purchase_rate
					print("valuation_cost_in_stock_uom",valuation_cost_in_stock_uom)
					total_item_cost=valuation_cost_in_stock_uom*stock_qty
					input_cost_for_raw_material="Yes"
					total_rm_qty=qty*stock_qty
					data.append([default_bom_available,bom,sales_item_code,item_name,
					qty,stock_qty,total_rm_qty,stock_uom,round(float(stock_valuation_price),2),
					 round(float(last_purchase_rate),2),purchase_uom,
					 round(float(conversion_factor),2), round(float(valuation_cost_in_stock_uom),2),
					 round(float(total_item_cost),2),input_cost_for_raw_material,actual_qty,pending_po_qty])
	data=test(data)
	
	return columns, data

def test(data):
	array1=[]
	for d in data:
		if d[13]==0:
			if d[1] not in array1:
				array1.append(d[1]) 
	#print("array1",array1)
	for a in array1:
		for d in data:
			if a==d[1]:
				d[14]="No"
			else:
				d[14]="Yes"
	print("data",data)
	return data

def get_columns():
	return [
	_("Default BOM Available?") +"::110",
	_("Default BOM") + "::110",
	_("Sales Item") + ":Link/Item:110",
	_("Raw Items") + ":Link/Item:110",
	_("FG SO Qty") + "::110",
	_("Qty in Stock UOM") + "::110",
	_("Total RM Qty") + "::110",
	_("Stock UOM") + ":Link/UOM:110",
	_("Valuation Rate in Stock UOM") + "::110",
	_("Purchase Rate") + "::110",
	_("Purchase UOM") + "::110",
	_("Conversion Factor Purchase UOM to Stock UOM") + "::110",
	_("Purchase/Valuation Cost in Stock UOM") + "::130",
	_("Total Item Cost") + "::110",
	_("Inputs costs for all raw material available?") + "::130",
	_("Stock As On Date") + "::110",
	_("Balance Qty") + "::110"
	
	
	

	

]

def warehouse_qty_details(item_code,warehouse):
    warehouse_qty_details = frappe.db.sql("""select actual_qty from `tabBin`  where
    			item_code = '"""+item_code+"""' and warehouse = '"""+warehouse+"""'
    			""", as_dict=1)
    print("warehouse_qty_details",warehouse_qty_details)
    return warehouse_qty_details

def fetch_po_details(item_code,warehouse):
    stock_qty_of_po =frappe.db.sql("""select sum(poi.stock_qty) as quantity
	from  `tabPurchase Order` po,`tabPurchase Order Item` poi  
	where po.name=poi.parent and po.docstatus!=2 and
	poi.item_code='"""+item_code+"""' and poi.warehouse = '"""+warehouse+"""' """, as_dict=1)
    print("stock_qty_of_po",stock_qty_of_po[0]['quantity'])
    if stock_qty_of_po[0]['quantity'] is None:
        stock_qty_of_po[0]['quantity']=0
    else:
    	stock_qty_of_po[0]['quantity']=stock_qty_of_po[0]['quantity']	
    received_stock_qty_of_po =frappe.db.sql("""select sum(received_stock_qty) as received_qty from `tabPurchase Receipt Item`  
    where item_code='"""+item_code+"""' and warehouse = '"""+warehouse+"""' """, as_dict=1)
    print("received_stock_qty_of_po",received_stock_qty_of_po[0]['received_qty'])
    if received_stock_qty_of_po[0]['received_qty'] is None:
        print("enterd in if")
        received_stock_qty_of_po[0]['received_qty']=0
    
    else:
       received_stock_qty_of_po[0]['received_qty']=received_stock_qty_of_po[0]['received_qty']
    balance_qty=stock_qty_of_po[0]['quantity']-received_stock_qty_of_po[0]['received_qty']
    print("balance_qty",balance_qty)
    return balance_qty


def sales_item_details(company,sales_order):
	sales_item_details = frappe.db.sql("""select si.item_code,si.stock_uom,si.qty
	from `tabSales Order` so, `tabSales Order Item` si 
				where so.name = si.parent and so.docstatus = 1 and 
				so.company = '"""+company+"""' and si.parent = '"""+sales_order+"""'
				order by
					si.item_code""", as_dict=1)
	return sales_item_details

def get_conversion_factore(item_code,purchase_uom):
    	
	#print "item_code==============",item_code
	conversion = frappe.db.sql("""select conversion_factor from `tabUOM Conversion Detail` where parent = %s and uom = %s """,(item_code,purchase_uom), as_dict=1)
	
	return conversion

def get_stock_ledger_entry(item_code):
	stock_entry = ""
	stock_entry = frappe.db.sql("""select name,valuation_rate, item_code  
					from  
						`tabStock Ledger Entry` 
					where 
						name = (select max(name) from `tabStock Ledger Entry` where item_code =%s)
							""",item_code,as_dict=1)
	#print "stock_entry===========",stock_entry
	return stock_entry


def bom_details(company , bom):
    #conditions = get_conditions(company , bom)
	#print ("conditions-------------",conditions)
	bom_detail = frappe.db.sql("""select
				bo.name as bom_name, bo.company, bo.item as bo_item, bo.quantity as bo_qty,
					bo.project,bi.item_name,bi.item_code as bi_item,bi.description, 
					bi.stock_qty as bi_qty,bi.stock_uom
			from
				`tabBOM` bo, `tabBOM Explosion Item` bi
			where
				bo.name = bi.parent and bo.is_active=1 and bo.docstatus = 1 and 
				bo.company = '"""+company+"""' and bi.parent = '"""+bom+"""'

			order by
				bi.item_code""", as_dict=1)
	return bom_detail

def get_item_details(item_code):
	item_detail = frappe.db.sql("""select
											purchase_uom,valuation_rate,item_group,last_purchase_rate
									from
											`tabItem`
									where
											item_code = %s""",(item_code), as_dict =1)
	return item_detail

def get_number_of_purchase(item_code):
	purchase = frappe.db.sql("""select
										count(parent) as num_of_purchase,avg(rate) as avg_purchase,MAX(rate) as max_purchase,
										MIN(rate) as min_purchase
								from
										`tabSales Order Item`
								where
										item_code = %s and docstatus = 1""",(item_code), as_dict=1)
	return purchase

def get_sales_order_no(item_code):
    	#print "item code-------------------",item_code
	purchase_name_count = 0
	total_rate = 0.0
	lowest_rate = 0.0
	highest_rate = 0.0
	avg_rate = 0.0
	sales_order_lha = []
	sales_order = frappe.db.sql("""select 
						poi.item_code,poi.conversion_factor,poi.rate,poi.parent
					from 
						`tabSales Order Item` poi 
					where 
						poi.item_code = %s  and docstatus = 1
						""",item_code, as_dict =1)

	lowest_purchase_item_rate = frappe.db.sql("""SELECT parent,rate,item_code,conversion_factor from `tabSales Order Item`  where rate = (select min(rate) from `tabSales Order Item` where item_code = %s and docstatus =1) and item_code = %s and conversion_factor = (select max(conversion_factor) from `tabSales Order Item` where item_code = %s and docstatus =1) and docstatus =1""",(item_code,item_code,item_code), as_dict =1)

	highest_purchase_item_rate = frappe.db.sql("""SELECT parent,rate,item_code,min(conversion_factor) as conversion_factor
	from `tabSales Order Item`  
	where rate = (select max(rate) from `tabSales Order Item` where item_code = %s and docstatus =1) 
		and item_code = %s and docstatus =1""",(item_code,item_code), as_dict =1)
	if highest_purchase_item_rate:
		for highest in highest_purchase_item_rate:
			if highest.rate is not None and highest.conversion_factor is not None:
				highest_rate = highest.rate / highest.conversion_factor
	#print "highest rate -------------",highest_rate
	
	if lowest_purchase_item_rate:
		for lowest in lowest_purchase_item_rate:
			if lowest.rate is not None and lowest.conversion_factor is not None:
				lowest_rate = lowest.rate / lowest.conversion_factor
	#print "lowest_rate--------------",lowest_rate
	if sales_order:
		for purchase in sales_order:
			purchase_name_count = purchase_name_count + 1
			conversion_factor = purchase.conversion_factor
			rate = purchase.rate
			rate_with_conversion = rate / conversion_factor
			total_rate += rate_with_conversion
	if purchase_name_count > 0.0:
		avg_rate = total_rate/purchase_name_count
	highest_rate = round(float(highest_rate),2)
	lowest_rate = round(float(lowest_rate),2)
	avg_rate = round(float(avg_rate),2)
	purchase_name_count = round(float(purchase_name_count),2)
	sales_order_lha.append(
				{
				"highest_rate":highest_rate,
				"lowest_rate":lowest_rate,
				"avg_rate":avg_rate,
				"purchase_name_count":purchase_name_count
				})
	
	return sales_order_lha
