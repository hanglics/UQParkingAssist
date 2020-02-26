import requests
from bs4 import BeautifulSoup
import math
import datetime

UQFEED = None


def getUQFeed():
    print("Updating UQ Feed At: " + str(datetime.datetime.now()))
    response = requests.get("https://pg.pf.uq.edu.au")
    if response.status_code == 200:
        global UQFEED
        UQFEED = response.content
        return UQFEED
    else:
        getUQFeed()


def getResponse(PARKINGLOTINFO, lot, location, userType="S"):
    parkinginfo = parseFeed(PARKINGLOTINFO, location)
    return getUserSpecificResponse(parkinginfo, userType, lot)


def getUserSpecificResponse(parkinginfo, userType, lot):
    res = []
    if lot != "":
        temp = []
        for each in parkinginfo:
            lotParts = []
            realLot = each["lot"]
            if " " in realLot:
                lotParts = realLot.split(" ")
            else:
                lotParts.append(realLot)
            if lot in lotParts:
                temp.append(each)
            for t in temp:
                if userType in t["type"]:
                    res.append(t)
        res.sort(key=lambda x: x["distance"])
        return res
    else:
        parkinginfo.sort(key=lambda x: x["distance"])
        for each in parkinginfo:
            if userType in each["type"]:
                res.append(each)
        return res


def getDistance(my, park):
    distance = math.sqrt(math.pow((float(my[0]) - float(park[0])), 2) + math.pow((float(my[1]) - float(park[1])), 2))
    return distance


def parseFeed(PARKINGLOTINFO, location):
    data = []
    status = []
    soup = BeautifulSoup(UQFEED, "html.parser")
    table = soup.table
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele])
    for each in data:
        if len(each) != 0:
            status.append(each)
    P10Status = None
    for s in status:
        if s[0] == "P10":
            P10Status = s[1]
    for parking in PARKINGLOTINFO:
        for stat in status:
            if parking["lot"] == stat[0]:
                parking["status"] = stat[1]
            elif "P10" in parking["lot"]:
                parking["status"] = P10Status
        myGeo = location.split(",")
        parkGeo = parking["geo"].split(",")
        distance = getDistance(myGeo, parkGeo)
        parking["distance"] = distance
    return PARKINGLOTINFO
