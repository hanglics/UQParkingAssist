import requests
from bs4 import BeautifulSoup
import json
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


def getResponse(PARKINGLOTINFO, lot, location, CONFIG, userType="S"):
    parkinginfo = parseFeed(PARKINGLOTINFO, location, CONFIG)
    res = getUserSpecificResponse(parkinginfo, userType, lot)
    return res


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
                if userType in t["type"] and t["status"] != "FULL":
                    res.append(t)
        if len(res) > 0:
            res.sort(key=lambda x: x["distance"])
        return res
    else:
        for each in parkinginfo:
            if userType in each["type"] and each["status"] != "FULL":
                res.append(each)
        if len(res) > 0:
            res.sort(key=lambda x: x["distance"])
        for park in parkinginfo:
            if park["distance"] > 1000:
                park["distance"] = "{:.1f}".format(float(park["distance"] / 1000)) + " kilometers"
            else:
                park["distance"] = "{} meters".format(park["distance"])
        return res


def getDistance(my, park, CONFIG):
    distance = None
    duration = None
    response = requests.get("{}?origins={},{}&destinations={},{}&key={}".format(CONFIG["google_map_url"], my[0], my[1], park[0], park[1], CONFIG["google_map_key"]))
    if response.status_code == 200:
        content = json.loads(response.content)
        distance = content["rows"][0]["elements"][0]["distance"]["value"]
        duration = content["rows"][0]["elements"][0]["duration"]["text"]
    else:
        getDistance(my, park, CONFIG)
    return distance, duration


def parseFeed(PARKINGLOTINFO, location, CONFIG):
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
        distance, duration = getDistance(myGeo, parkGeo, CONFIG)
        parking["distance"] = distance
        parking["duration"] = duration
    return PARKINGLOTINFO
