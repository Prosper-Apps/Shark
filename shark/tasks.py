from pydoc import doc
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

def all():
    pass


def daily():
    print("Hel000>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    po_details = frappe.db.sql("""select name from tabPurchase Order where status="To Receive and Bill" AND schedule_date < DATE_SUB(CURDATE(), INTERVAL 30 DAY) """ , as_dict=1)
    print("po_data",po_details)
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Hello Im created")
    if po_details!=[]:
        for po_data in po_details:
            po_name=po_data['name']
            print("po_name",po_name)
            doc=frappe.get_doc("Purchase Order",po_name)
            doc.cancel()
            print("cancelled succesfully")