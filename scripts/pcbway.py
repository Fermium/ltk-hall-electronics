import requests
import time

def getPCBWayPrice(quantity, uniqueparts, smtparts=0, bgaparts=0, thtparts=0):
    url  = "https://www.pcbway.com/member/ajax/ajaxorder.aspx?act=GetDeliveryDays"
    url += "&t=" + str(int(time.time()))
    url += "spanPCBNos=&partVias=Turnkey"
    url += "&txtBoardNum=" + str(quantity)
    url += "&txtICType=" + str(uniqueparts)
    url += "&txtPadsNum=" + str(smtparts)
    url += "&txtBGA=" + str(bgaparts)
    url += "&txtHolesNum=" + str(thtparts)
    url += "&boardType=Single+pieces"
    url += "&hidAssemblySide=Single+Side"
    url += "&txtSMTNote="
    url += "&radBoardType=Single+PCB&hidEdgeRails=Yes&iptEdgeRailsContent=&hidRouteProcess=--&txtPinBanNum=1&hidLength=&hidWidth=&hidNum=&txtSelNum=&hidLayers=2&hidCopperlayer=--&hidSoldermask=--&hidSilkscreenLegend=--&FR4Type=FR-4&hidFR4TG=TG130&radBoardThickness=1.6&radLineWeight=6%2F6mil&radVias=0.3&radSolderColor=Green&radFontColor=White&radGoldfingers=No&hidChamferedborder=No&radPlatingType=Immersion+gold&radSolderCover=Tenting+vias&radCopperThickness=1+oz+Cu&radInsideThickness=1&hidPlatedHalfHole=No&hidSidePlating=No&hidCustomStackup=No&hidImpedanceControl=No&hidCountersink=No&txtPCBNote=&selShip=1&selShipCountry=0&hidStenciltotal=0&hidSMTtotal=5519&hidDaySMT=&hidDeliveryDaysSMT=&hidSMTQty=&hidMoney=&hidTmpNO=&hidDay=&hidShipMoney=0&hidShipName=DHL&hidCountryName=&hidCountryId=0&hidWebSaveMoney=&userId=0&saveact=save&hidDeliveryDays=&pagetype=3&seqtype=0&txtMail="
    url += "&_=" + str(int(time.time()))
    
    r = requests.get(url)
    r.status_code
    price = int(r.json()[0]["Price"])
    return price
