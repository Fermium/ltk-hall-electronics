#!/usr/bin/python3
import csv
import glob

partFileslist = glob.glob('../exports/*/purchase_files/BOM/*.csv')

print("Opening files:")
for file in partFileslist:
    print("\t", file)
    
print("\n\n")

partslist = []
for file in partFileslist:
    with open(file, 'rt', encoding='latin-1') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            partslist.append(row)
            

# Merge specific values (like Resistance and Capacitance) into "Value"
for row in partslist:
    if row.get("Value", "") == "":
        row["Value"] = row.pop("Capacitance", "") + row.pop("Resistance", "")
    else:
        row.pop("Capacitance", "")
        row.pop("Resistance", "")

# Check for missing suppliers
for row in partslist:
    if row.get("Supplier 1", "") is ""  :
        print("Supplier missing for part:")
        print("\t", {k: v for k, v in row.items() if v})
        row["Supplier 1"] = "N/A"
    if row.get("Supplier Part Number 1", "") is "" :
        print("Supplier Part Number missing for part:")
        print("\t", {k: v for k, v in row.items() if v})
        row["Supplier Part Number 1"] = "N/A"
    if row.get("Manufacturer Part Number", "") is "":
        print("Manufacturer part number  missing for part:")
        print("\t", {k: v for k, v in row.items() if v})
        row["Manufacturer Part Number"] = "N/A"
    if row.get("Manufacturer", "") is "":
        print("Manufacturer data missing for part:")
        print("\t", {k: v for k, v in row.items() if v})
        row["Manufacturer"] = "N/A"

print("\n\n")

# Write "N/A" in empty fields
for i,row in enumerate(partslist):
    for key in row:
        if row[key] == "":
            partslist[i][key] = "N/A"
            

itemsBySupplier = {}    

# initialize dict with suppliers
for row in partslist:
    itemsBySupplier[row["Supplier 1"]] = {}
    
# initialize dict by part keys inside dict of suppliers
for supplier in itemsBySupplier:
    for row in partslist:
        if row["Supplier 1"] == supplier:
            itemsBySupplier[supplier][row["Supplier Part Number 1"]] = {}
            itemsBySupplier[supplier][row["Supplier Part Number 1"]]["QNT"] = 0
            
for row in partslist:
    itemsBySupplier[row["Supplier 1"]][row["Supplier Part Number 1"]]["QNT"] += int(row["Quantity"])
    itemsBySupplier[row["Supplier 1"]][row["Supplier Part Number 1"]]["MPN"] = row["Manufacturer Part Number"]
    itemsBySupplier[row["Supplier 1"]][row["Supplier Part Number 1"]]["MN"] = row["Manufacturer"]
    itemsBySupplier[row["Supplier 1"]][row["Supplier Part Number 1"]]["SKU"] = row["Supplier Part Number 1"]
    
for supplier in itemsBySupplier:
    print(supplier, ":")
    print("\t", itemsBySupplier[supplier])
    
