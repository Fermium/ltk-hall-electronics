#!/usr/bin/python3
import csv
import os
import glob
from  octopart import octopart_url, datasheet_url, disty_stock, disty_price
import re
import sys
import math



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
            
################################### ASK FOR AMOUNT OF PRODUCTS TO manufacturer

productsToManufacture = input("Number of products to manufacture: ")

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
        row["Pads"] = "N/A"

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

#parts that can be trashed easly
disposable = {}
    
for row in partslist:
    # match regular expressions
    thtpads = re.findall(r'\d+ THT', row["Pads"])
    smdpads = re.findall(r'\d+ SMD', row["Pads"])
    # if there are pads, add them to board count
    if thtpads:
        boardstats[row["board"]]["THT Pads"] += (float(thtpads[0].replace(" THT", "")) * float(row["Quantity"]))
        boardstats[row["board"]]["Unique THT parts"] += 1
        boardstats[row["board"]]["Total THT parts"] += float(row["Quantity"])
        # THT parts are not disposable
        disposable[row["Supplier Part Number 1"]] = False


    if smdpads:
        pads = (float(smdpads[0].replace(" SMD", "")) * float(row["Quantity"]))
        boardstats[row["board"]]["SMD Pads"] += pads
        boardstats[row["board"]]["Unique SMD parts"] += 1
        boardstats[row["board"]]["Total SMD parts"] += float(row["Quantity"])
        
        if pads <= 3 and not thtpads:
            disposable[row["Supplier Part Number 1"]] = True
        else:
            disposable[row["Supplier Part Number 1"]] = False

    
    if not smdpads and not thtpads:
        disposable[row["Supplier Part Number 1"]] = False

    
    boardstats[row["board"]]["Total unique parts"] += 1
    boardstats[row["board"]]["Total parts"] += float(row["Quantity"])
    
#################################### 

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
    itemsBySupplier[row["Supplier 1"]][row["Supplier Part Number 1"]]["qnt"] += float(row["Quantity"])
    itemsBySupplier[row["Supplier 1"]][row["Supplier Part Number 1"]]["mnt"] = row["Manufacturer Part Number"]
    itemsBySupplier[row["Supplier 1"]][row["Supplier Part Number 1"]]["brand"] = row["Manufacturer"]
    itemsBySupplier[row["Supplier 1"]][row["Supplier Part Number 1"]]["sku"] = row["Supplier Part Number 1"]

#################################### GET PRICES FROM OCTOPART

#for supplier in itemsBySupplier:
#    print(supplier, ":")
#    print("\t", itemsBySupplier[supplier])

print("Fetching component data from octopart...")
    
for supplier in itemsBySupplier:
    for sku in itemsBySupplier[supplier]:
        itemsBySupplier[supplier][sku]["price"] = disty_price(supplier, sku)
        #print(sku,"price:", itemsBySupplier[supplier][sku]["price"], "EUR")

        
for supplier in itemsBySupplier:
    for sku in itemsBySupplier[supplier]:
        stock_count = disty_stock(supplier, sku)
        itemsBySupplier[supplier][sku]["stock"] = stock_count
        #print(sku,"stock:", stock_count)

print("\n")

#for supplier in itemsBySupplier:
#    print(supplier, ":")
#    print("\t", itemsBySupplier[supplier])

################################### MULTIPLY QUANTITY

try:
    productsToManufacture = float(productsToManufacture)
except ValueError:
    print("Invalid Number!")
    sys.exit(1)


for supplier in itemsBySupplier:
    for sku in itemsBySupplier[supplier]:
        itemsBySupplier[supplier][sku]["qnt"] = math.ceil(itemsBySupplier[supplier][sku]["qnt"] * productsToManufacture)


#################################### DISPOSABLE ITEMS CALCULATIONS

# mark items as non-disposable based on price
for supplier in itemsBySupplier:
    for sku in itemsBySupplier[supplier]:
        try:
            float(itemsBySupplier[supplier][sku]["stock"])
            if disposable[sku] == True:
                if itemsBySupplier[supplier][sku]["price"] >= 0.15:
                    disposable[sku] = False
                    print("Item", sku, "was marked as non-disposable due to high price of", itemsBySupplier[supplier][sku]["price"])
        except:
            pass
            

# Increment quantity of disposable items based on pcbway rules
for supplier in itemsBySupplier:
    for sku in itemsBySupplier[supplier]:
        if disposable[sku]:
            # Follow PCBWAY pcb guidelines for minimun quantities
            itemsBySupplier[supplier][sku]["qnt"] = itemsBySupplier[supplier][sku]["qnt"] + 30
            itemsBySupplier[supplier][sku]["qnt"] = max(itemsBySupplier[supplier][sku]["qnt"], 50)
            

        

################################### CALCULATE TOTAL PRICE, CHECK IF STOCK IS OK

for supplier in itemsBySupplier:
    for sku in itemsBySupplier[supplier]:
        try:
            float(itemsBySupplier[supplier][sku]["price"])
            itemsBySupplier[supplier][sku]["price_tot"] = float(itemsBySupplier[supplier][sku]["price"]) * float(itemsBySupplier[supplier][sku]["qnt"])
        except ValueError:
            itemsBySupplier[supplier][sku]["price_tot"] = "N/A"
            
for supplier in itemsBySupplier:
    for sku in itemsBySupplier[supplier]:
        try:
            float(itemsBySupplier[supplier][sku]["stock"])
            if itemsBySupplier[supplier][sku]["stock"] >= itemsBySupplier[supplier][sku]["qnt"]:
                itemsBySupplier[supplier][sku]["stock_check"] = "pass"
            else:
                itemsBySupplier[supplier][sku]["stock_check"] = "fail"
        except ValueError:
            itemsBySupplier[supplier][sku]["stock_check"] = "N/A"
            

#################################### EXPORTING AND PRINTING

outdir = "../exports/combined/"
by_supplierdir = os.path.join(outdir + "/by_supplier")
#create output dir
if not os.path.exists(by_supplierdir):
    os.makedirs(by_supplierdir)
#delete all files in the output dir
for f in glob.glob(outdir + "**/*"):
    try:
        os.remove(f)
    except:
        pass
# Write basic CSV bom of items to by
for supplier in itemsBySupplier:
    with open(os.path.join(by_supplierdir + "/" , supplier + ".csv"), 'w') as csvfile:
        fieldnames = ["sku", "qnt", "price", "price_tot", "stock", "stock_check"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval='', extrasaction='ignore')
        writer.writeheader()
        for sku in itemsBySupplier[supplier]:
            writer.writerow(itemsBySupplier[supplier][sku])
            
            
#################################### EXPORTING AND PRINTING for quickbuy

by_supplierdir_quickbuy_auto = os.path.join(outdir + "/quickbuy" + "/auto")
#create output dir
if not os.path.exists(by_supplierdir_quickbuy_auto):
    os.makedirs(by_supplierdir_quickbuy_auto)
#delete all files in the output dir
for f in glob.glob(by_supplierdir_quickbuy_auto + "**/*"):
    try:
        os.remove(f)
    except:
        pass
        
by_supplierdir_quickbuy_manual = os.path.join(outdir + "/quickbuy" + "/manual")
#create output dir
if not os.path.exists(by_supplierdir_quickbuy_manual):
    os.makedirs(by_supplierdir_quickbuy_manual)
#delete all files in the output dir
for f in glob.glob(by_supplierdir_quickbuy_manual + "**/*"):
    try:
        os.remove(f)
    except:
        pass
    


for supplier in itemsBySupplier:
    csvfile_manual = open(os.path.join(by_supplierdir_quickbuy_manual + "/"  +  supplier + ".csv"), 'w')
    csvfile_auto = open(os.path.join(by_supplierdir_quickbuy_auto  + "/" + supplier + ".csv"), 'w')
    
    fieldnames = ["sku", "qnt"]
    
    delimiter = ","
    if supplier == "Mouser":
        delimiter = "|"

    writer_auto = csv.DictWriter(csvfile_auto, fieldnames=fieldnames, restval='', extrasaction='ignore', delimiter=delimiter)
    writer_manual =  csv.DictWriter(csvfile_manual, fieldnames=fieldnames, restval='', extrasaction='ignore', delimiter=delimiter)
    
    for sku in itemsBySupplier[supplier]:
        if itemsBySupplier[supplier][sku]["stock_check"] is "pass":
            writer_auto.writerow(itemsBySupplier[supplier][sku])
        else:
            writer_manual.writerow(itemsBySupplier[supplier][sku])

#################################### GET PRICES OF ASSEMBLY FROM PCBWAY
"""


from pcbway import getPCBWayPrice

for board in boardstats:
    boardstats[board]["prices"] = []
    boardstats[board]["Unit prices"] = []
    boardstats[board]["quantities"] = [10,20,30,40,50,60,70,80,80,100,150,200,250,300,400,500,600,700,800,900,1000]
    for quantity in boardstats[board]["quantities"]:
        uniqueparts = boardstats[board]["Total unique parts"]
        smtparts = boardstats[board]["Total SMD parts"]
        bgaparts = 0
        thtparts =  boardstats[board]["Total THT parts"]
        price = getPCBWayPrice(quantity, uniqueparts, smtparts, bgaparts, thtparts)
        boardstats[board]["prices"].append(price) 
        boardstats[board]["Unit prices"].append(price/quantity) 
"""
#################################### STATS MARKDOWN REPORT

reportFileName = outdir + "component_count_report.md"


if os.path.exists(reportFileName):
    os.remove(reportFileName)
    
reportFile = open(reportFileName, "a")

print("# Component and pad count", "\n", file=reportFile)
for board in boardstats:
    print("\n", file=reportFile)
    print("###", board, "board", ":", "\n", file=reportFile)
    print("|", "Stat", "|", "Count", "|", file=reportFile)
    print("| --- | --- |", file=reportFile)
    for stat in boardstats[board]:
        print("|", stat, "|", boardstats[board][stat], "|", file=reportFile)
    print("\n", file=reportFile)
    """
    print("|", "Quantity", "|", "Assembly price (pcbway)", "|", "Unit Price", "|", file=reportFile)
    print("| --- | --- | --- |", file=reportFile)
    for index, quantity in enumerate(boardstats[board]["quantities"]):
        print("|", quantity, "|", boardstats[board]["prices"][index], "|", boardstats[board]["Unit prices"][index], file=reportFile)
    print("\n", file=reportFile)
    print("![" + board + " board" + "](" + board + ".png"+")", file=reportFile)
    print("\n", file=reportFile)
    print("![" + board + " board" + "](" + board + "_zoomed" +  ".png"+")", file=reportFile)
    """
print("Generated board stats report:", reportFileName)

#################################### PRINT PRICE GRAPHS
"""
import matplotlib.pyplot as plt

index = 1

for board in boardstats:
    plt.figure(index)
    plt.title(board + " board PCBWay cost estimation") # subplot 211 title
    index += 1
    plt.plot(boardstats[board]["quantities"], boardstats[board]["Unit prices"])
    plt.xlabel("Quantity")
    plt.ylabel("Unit Price")
    plt.savefig(outdir + board + ".png")

for board in boardstats:
    plt.figure(index)
    plt.title(board + " board PCBWay cost estimation (zoomed)") # subplot 211 title
    index += 1
    plt.plot(boardstats[board]["quantities"][:5], boardstats[board]["Unit prices"][:5])
    plt.xlabel("Quantity")
    plt.ylabel("Unit Price")
    plt.savefig(outdir + board + "_zoomed" ".png")
"""
import subprocess
subprocess.call(['./generate_html.sh']) 
