from __future__ import unicode_literals
import frappe
from frappe import _, throw, msgprint, utils
from frappe.utils import cint, flt, cstr, comma_or, getdate, add_days, getdate, rounded, date_diff, money_in_words
from frappe.model.mapper import get_mapped_doc
from frappe.model.naming import make_autoname
from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import get_party_account_currency
from frappe.desk.notifications import clear_doctype_notifications
from datetime import datetime
import sys
import os
import operator
import frappe
import json
import time
import math
import base64
import ast
import PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader,PdfFileMerger
from shutil import copyfile
parent_list = []

@frappe.whitelist()
def make_bom_for_boq_lite(source_name, target_doc=None):
	boq_record = frappe.get_doc("BOQ Light", source_name)
	company = boq_record.company
	name = boq_record.name

	boq_lite_items = frappe.db.sql("""select distinct boqi.immediate_parent_item as bom_item from `tabBOQ Light Item` boqi where boqi.parent=%s""", boq_record.name,  as_dict=1)

	if boq_lite_items:
		raw_boms = []
		for parent in boq_lite_items:
			bom_main_item = parent.bom_item
			boq_records = frappe.db.sql("""select * from `tabBOQ Light Item` where parent=%s and immediate_parent_item=%s and is_raw_material='No' order by immediate_parent_item desc""", (boq_record.name,bom_main_item), as_dict=1)
			#print "bom_main_item--------", bom_main_item
			
			if not boq_records:
				bom_qty = 1
				raw_boms.append(bom_main_item)
				boq_record_bom_items = frappe.db.sql("""select boqi.item_code as qi_item, boqi.qty as qty, boqi.is_raw_material as is_raw_material from `tabBOQ Light Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s order by boqi.item_code""" , (source_name, bom_main_item), as_dict=1)

				if boq_record_bom_items:

					outer_json = {
						"company": company,
						"doctype": "BOM",
						"item": bom_main_item,
						"quantity": bom_qty,
						"pch_boq_lite_reference": name,
						"items": []
						}

					for record in boq_record_bom_items:
						item = record.qi_item
						qty = record.qty
						if item:
							item_record = frappe.get_doc("Item", item)
							innerJson ={
								"doctype": "BOM Item",
								"item_code": item,
								"description": item_record.description,
								"uom": item_record.stock_uom,
								"stock_uom": item_record.stock_uom,
								"qty": qty
								}
							outer_json["items"].append(innerJson)

					if outer_json["items"]:
						doc = frappe.new_doc("BOM")
						doc.update(outer_json)
						doc.save()
						frappe.db.commit()
						doc.submit()
						docname = doc.name
						frappe.msgprint(_("BOM Created - " + docname))
		if raw_boms:
			#print "raw_boms--------------", raw_boms
			global parent_list
			parent_list = []
			for bom_item in raw_boms:
				parent = frappe.db.sql("""select immediate_parent_item as bom_main_item  from `tabBOQ Light Item` where parent=%s and item_code=%s""", (boq_record.name,bom_item), as_dict=1)
				if parent:
					for main_item in parent:
						bom_main_item = main_item.bom_main_item
						#print "*****parent for*****",bom_item, bom_main_item
						if bom_main_item not in parent_list:
							parent_list.append(bom_main_item)
							submit_assembly_boms(name,bom_main_item,company)
					#print "*****parent_list*****", parent_list

def submit_assembly_boms(name,bom_main_item,company):
    
	boq_record_bom_items = frappe.db.sql("""select boqi.item_code as qi_item, boqi.qty as qty, boqi.is_raw_material as is_raw_material from `tabBOQ Light Item` boqi where boqi.parent = %s and boqi.immediate_parent_item = %s order by boqi.item_code""", (name, bom_main_item),as_dict=1)
	bom_qty = 1
	if boq_record_bom_items:
		outer_json = {
			"company": company,
			"doctype": "BOM",
			"item": bom_main_item,
			"quantity": bom_qty,
			"pch_boq_lite_reference": name,
			"items": []
			}

		for record in boq_record_bom_items:
			item = record.qi_item
			qty = record.qty
			if item:
				item_record = frappe.get_doc("Item", item)
				innerJson ={
					"doctype": "BOM Item",
					"item_code": item,
					"description": item_record.description,
					"uom": item_record.stock_uom,
					"stock_uom": item_record.stock_uom,
					"qty": qty
					}
				outer_json["items"].append(innerJson)
		if outer_json["items"]:
			doc = frappe.new_doc("BOM")
			doc.update(outer_json)
			'''
			name_bom = "BOM-"+str(bom_main_item)+"-"
			check_status = frappe.db.sql("""select max(name) from `tabBOM` where name LIKE '"""+name_bom+"%""'""", as_dict = 1)
			print "check_status-------------",check_status
			'''
			doc.save()
			frappe.db.commit()
			doc.submit()
			docname = doc.name
			frappe.msgprint(_("BOM Created - " + docname))

		parent = frappe.db.sql("""select immediate_parent_item as bom_main_item  from `tabBOQ Light Item` where parent=%s and item_code=%s""", (name,bom_main_item), as_dict=1)
		for main_item in parent:
			parent_item = main_item.bom_main_item

			multi_parent_list = check_multiple_parent_items(name,parent_item)
			#print "***2nd**parent for*****", bom_main_item, parent_item
			if multi_parent_list:
				for parent in multi_parent_list:
					if parent not in parent_list:
						parent_list.append(parent)
						submit_assembly_boms(name,parent,company)
			else:
				if parent_item  not in parent_list:
					parent_list.append(parent_item)
					submit_assembly_boms(name,parent_item,company)



def check_multiple_parent_items(name,parent_item):
	sub_parent_items = []
	parent_items = frappe.db.sql("""select item_code as bom_main_item  from `tabBOQ Light Item` where parent=%s and immediate_parent_item=%s""", (name,parent_item), as_dict=1)
	if parent_items:
		for parent in parent_items:
			sub_parent = parent['bom_main_item']
			sub_items = frappe.db.sql("""select * from `tabBOQ Light Item` where parent=%s and immediate_parent_item=%s""", (name,sub_parent), as_dict=1)
			if sub_items and sub_parent not in parent_list and sub_parent not in sub_parent_items:
				sub_parent_items.append(sub_parent)
				check_multiple_parent_items(name,sub_parent)
	sub_parent_items.reverse()
	sub_parent_items.append(parent_item)
	return sub_parent_items

@frappe.whitelist()
def get_stock_uom(item_code):
	records = frappe.db.sql("""select stock_uom as uom from `tabItem` where item_code = %s""", (item_code))

	if records:
#		frappe.msgprint(_(records[0].warehouse))
#		return records[0].warehouse
		return records
	else:
		return


@frappe.whitelist()
def update_boq_lite_item(item_code,name,is_raw_material):
	records = frappe.db.sql("""update `tabBOQ Light Item` set is_raw_material = '"""+ str(is_raw_material)+"""' where parent=%s and item_code=%s""", (name, item_code))
	frappe.db.commit()

@frappe.whitelist()
def get_sales_order_item_list(name):
	print("name",name)
	get_sales_order_item =frappe.db.sql("""select soi.item_code,soi.qty from `tabSales Order` so,
	`tabSales Order Item` soi where so.name=soi.parent and so.name='"""+name+"""' """, as_dict=1)
	print("get_sales_order_item_list",get_sales_order_item)
	return get_sales_order_item

@frappe.whitelist()
def get_qc_list(sales_order,item_code):
	print("item_code",item_code)
	get_qc_qty =frappe.db.sql("""select tqad.name,tqad.sales_order,
	tqadi.item_code,sum(tqadi.qc_qty_cleared) as qc_passed
	 from `tabQuality Assurance Document Items` tqadi,
	`tabQuality Assurance Document` tqad 
	where tqad.name=tqadi.parent and 
	tqad.sales_order='"""+sales_order+"""' and tqadi.item_code='"""+item_code+"""' """, as_dict=1)
	print("get_qc_qty............",get_qc_qty)
	return get_qc_qty