import requests
from bs4 import BeautifulSoup


def getUQFeed():
    response = requests.get("https://pg.pf.uq.edu.au")
    if response.status_code == 200:
        return response.content
    else:
        getUQFeed()


def parseFeed(content):
    soup = BeautifulSoup(content, "html.parser")
    print(soup.prettify())
