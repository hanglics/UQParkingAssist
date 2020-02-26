import requests
from bs4 import BeautifulSoup


def getUQFeed(PARKINGLOTINFO):
    response = requests.get("https://pg.pf.uq.edu.au")
    if response.status_code == 200:
        return parseFeed(response.content, PARKINGLOTINFO)
    else:
        getUQFeed(PARKINGLOTINFO)


def parseFeed(content, PARKINGLOTINFO):
    data = []
    status = []
    soup = BeautifulSoup(content, "html.parser")
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
            elif parking["lot"] == "P10":
                parking["status"] = P10Status
    return PARKINGLOTINFO
