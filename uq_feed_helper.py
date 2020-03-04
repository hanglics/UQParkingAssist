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
    parkinginfo = parseFeed(PARKINGLOTINFO)
    res = getUserSpecificResponse(parkinginfo, userType, lot, CONFIG, location)
    return res


def addDistances(parkinginfo, CONFIG, location):
    allGeo = []
    for each in parkinginfo:
        allGeo.append(each["geo"])
    geos = "|".join(allGeo)
    distanceinfo = getDistance(location, geos, CONFIG)
    distanceinfo = distanceinfo["rows"][0]["elements"]
    for ind, item in enumerate(parkinginfo):
        item["distance"] = distanceinfo[ind]["distance"]["value"]
        item["duration"] = distanceinfo[ind]["duration"]["text"]
    return parkinginfo


def getUserSpecificResponse(parkinginfo, userType, lot, CONFIG, location):
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
        parkinfo = addDistances(res, CONFIG, location)
        if len(parkinfo) > 0:
            parkinfo.sort(key=lambda x: x["distance"])
        else:
            parkinfo = []
        return parkinfo
    else:
        for each in parkinginfo:
            if userType in each["type"]:
                res.append(each)
        parkinfo = addDistances(res, CONFIG, location)
        if len(parkinfo) > 0:
            parkinfo.sort(key=lambda x: x["distance"])
        else:
            return []
        for park in parkinfo:
            if park["distance"] > 1000:
                park["distance"] = "{:.1f}".format(float(park["distance"] / 1000)) + " kilometers"
            else:
                park["distance"] = "{} meters".format(park["distance"])
        return parkinfo


def getDistance(my, park, CONFIG):
    response = requests.get("{}?origins={}&destinations={}&key={}".format(CONFIG["google_map_url"], my, park, CONFIG["google_map_key"]))
    if response.status_code == 200:
        content = json.loads(response.content)
        return content
    else:
        getDistance(my, park, CONFIG)


def parseFeed(PARKINGLOTINFO):
    res = []
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
    for each in PARKINGLOTINFO:
        if each["status"] != "FULL":
            res.append(each)
    return res
