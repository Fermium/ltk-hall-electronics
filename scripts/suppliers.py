#!/usr/bin/python3
import csv
import glob

partFileslist = glob.glob('../exports/*/purchase_files/BOM/*.csv')



print("Opening files:")
for file in partFileslist:
    print("\t", file)

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
    if row.get("Supplier 1", "") is "" or row.get("Supplier Part Number 1", "") is "" :
        print("Supplier data missing for part:")
        print("\t", {k: v for k, v in row.items() if v})

# Write "N/A" in empty fields
for row in partslist:
    for key in row:
        if row[key] == "":
            row[key] = "N/A"
            

for row in partslist:
    print(row)
    

    
