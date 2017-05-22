#!/usr/bin/python3
import csv
import os
import glob
from  octopart import octopart_url, datasheet_url, disty_stock, disty_price
import re


#################################### IMPORTING FILES
Fileslist = glob.glob('../exports/*/purchase_files/BOM/*.csv')

print("Opening files:")
for file in Fileslist:
    print("\t", file)
    
print("\n\n")

#List of non-unique parts that may be duplicated
partslist = []

for file in Fileslist:
    with open(file, 'rt', encoding='latin-1') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row["board"] = os.path.splitext(os.path.basename(file))[0].replace("BOM-csv-", "").replace("_board", "")
            partslist.append(row)

#################################### CLEANING, MERGING, CHECKING FOR PROBLEMS
# Merge specific values (like Resistance and Capacitance) into "Value"
for row in partslist:
    if row.get("Value", "") == "":
        row["Value"] = row.pop("Capacitance", "") + row.pop("Resistance", "")
    else:
        row.pop("Capacitance", "")
        row.pop("Resistance", "")


# Check for missing stuff
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
    if row.get("Pads", "") is "":
        print("Pads data missing for part:")
        print("\t", {k: v for k, v in row.items() if v})
        row["Manufacturer"] = "N/A"

print("\n\n")

# Write "N/A" in empty fields
for i,row in enumerate(partslist):
    for key in row:
        if row[key] == "":
            partslist[i][key] = "N/A"

#################################### CALCULATING BOARD STATISTICS
boardstats = {}

#initialize board stats
for row in partslist:
    boardstats[row["board"]] = {}
    boardstats[row["board"]]["THT Pads"] = 0
    boardstats[row["board"]]["SMD Pads"] = 0
    boardstats[row["board"]]["Unique SMD parts"] = 0
    boardstats[row["board"]]["Unique THT parts"] = 0
    boardstats[row["board"]]["Total SMD parts"] = 0
    boardstats[row["board"]]["Total THT parts"] = 0
    boardstats[row["board"]]["Total unique parts"] = 0
    boardstats[row["board"]]["Total parts"] = 0
for row in partslist:
    # match regular expressions
    thtpads = re.findall(r'\d+ THT', row["Pads"])
    smdpads = re.findall(r'\d+ SMD', row["Pads"])
    # if there are pads, att them to board count
    if thtpads:
        boardstats[row["board"]]["THT Pads"] += (int(thtpads[0].replace(" THT", "")) * int(row["Quantity"]))
        boardstats[row["board"]]["Unique THT parts"] += 1
        boardstats[row["board"]]["Total THT parts"] += int(row["Quantity"])


    if smdpads:
        boardstats[row["board"]]["SMD Pads"] += (int(smdpads[0].replace(" SMD", "")) * int(row["Quantity"]))
        boardstats[row["board"]]["Unique SMD parts"] += 1
        boardstats[row["board"]]["Total SMD parts"] += int(row["Quantity"])

    
    boardstats[row["board"]]["Total unique parts"] += 1
    boardstats[row["board"]]["Total parts"] += int(row["Quantity"])

#################################### CALCULATING PER-SUPPLIER BOM

itemsBySupplier = {}    

# initialize dict with suppliers
for row in partslist:
    itemsBySupplier[row["Supplier 1"]] = {}
    
# initialize dict by part keys inside dict of suppliers
for supplier in itemsBySupplier:
    for row in partslist:
        if row["Supplier 1"] == supplier:
            itemsBySupplier[supplier][row["Supplier Part Number 1"]] = {}
            itemsBySupplier[supplier][row["Supplier Part Number 1"]]["qnt"] = 0

#group by sku and sum quantities
for row in partslist:
    itemsBySupplier[row["Supplier 1"]][row["Supplier Part Number 1"]]["qnt"] += int(row["Quantity"])
    itemsBySupplier[row["Supplier 1"]][row["Supplier Part Number 1"]]["mnt"] = row["Manufacturer Part Number"]
    itemsBySupplier[row["Supplier 1"]][row["Supplier Part Number 1"]]["brand"] = row["Manufacturer"]
    itemsBySupplier[row["Supplier 1"]][row["Supplier Part Number 1"]]["sku"] = row["Supplier Part Number 1"]

#for supplier in itemsBySupplier:
#    print(supplier, ":")
#    print("\t", itemsBySupplier[supplier])
    
#for supplier in itemsBySupplier:
#    for sku in itemsBySupplier[supplier]:
#        itemsBySupplier[supplier][sku]["price"] = disty_price(supplier, sku)
#        
#for supplier in itemsBySupplier:
#    for sku in itemsBySupplier[supplier]:
#       stock_count = disty_stock(supplier, sku)
#        itemsBySupplier[supplier][sku]["stock"] = stock_count

#for supplier in itemsBySupplier:
#    print(supplier, ":")
#    print("\t", itemsBySupplier[supplier])


#################################### EXPORTING AND PRINTING

outdir = "../exports/combined/"
by_supplierdir = outdir + "by_supplier/"
#create output dir
if not os.path.exists(by_supplierdir):
    os.makedirs(by_supplierdir)
#delete all files in the output dir
for f in glob.glob(outdir + "**/*"):
    os.remove(f)
    
# Write basic CSV bom of items to by
for supplier in itemsBySupplier:
    with open(by_supplierdir  +  supplier + ".csv", 'w') as csvfile:
        fieldnames = ['sku', 'qnt']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval='', extrasaction='ignore')
        #writer.writeheader()
        for sku in itemsBySupplier[supplier]:
            writer.writerow(itemsBySupplier[supplier][sku])

#################################### GET PRICES OF ASSEMBLY FROM PCBWAY



from pcbway import getPCBWayPrice

for board in boardstats:
    boardstats[board]["prices"] = []
    boardstats[board]["Unit prices"] = []
    boardstats[board]["quantities"] = [10,20,30,40,50,75,100,150,200,250,300,350,400,450,500]
    for quantity in boardstats[board]["quantities"]:
        uniqueparts = boardstats[board]["Total unique parts"]
        smtparts = boardstats[board]["Total SMD parts"]
        bgaparts = 0
        thtparts =  boardstats[board]["Total THT parts"]
        price = getPCBWayPrice(quantity, uniqueparts, smtparts, bgaparts, thtparts)
        boardstats[board]["prices"].append(price) 
        boardstats[board]["Unit prices"].append(price/quantity) 

#################################### STATS REPORT

reportFileName = outdir + "component_count_report.md"


if os.path.exists(reportFileName):
    os.remove(reportFileName)
    
reportFile = open(reportFileName, "a")

print("# Component and pad count", "\n", file=reportFile)
for board in boardstats:
    print("\n","###", board, "board", ":", "\n", file=reportFile)
    print("|", "Stat", "|", "Count", "|", file=reportFile)
    print("| --- | --- |", file=reportFile)
    for stat in boardstats[board]:
        print("|", stat, "|", boardstats[board][stat], "|", file=reportFile)
    print("\n", file=reportFile)
    print("|", "Quantity", "|", "Assembly price (pcbway)", "|", "Unit Price", "|", file=reportFile)
    print("| --- | --- | --- |", file=reportFile)
    for index, quantity in enumerate(boardstats[board]["quantities"]):
        print("|", quantity, "|", boardstats[board]["prices"][index], "|", boardstats[board]["Unit prices"][index], file=reportFile)
        
print("Generated board stats report:", reportFileName)

for board in boardstats:
    import matplotlib.pyplot as plt
    plt.plot(boardstats[board]["quantities"], boardstats[board]["Unit prices"])
    plt.xlabel("Quantity")
    plt.ylabel("Unit Price")
    plt.savefig(outdir + board + ".png")
