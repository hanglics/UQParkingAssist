from uq_feed_helper import *
from flask import Flask, request
from flask_restful import Resource, Api
from flask_jsonpify import jsonpify
from middleware import *
from waitress import serve
import sys
import json


print("----------------------------------")
print("Loading Parking Lot Info...")
f = open("ParkingAddressMapper.json", "r")
PARKINGLOTINFO = json.loads(f.read())
f.close()
print("Loaded!")
print("----------------------------------")


def main():
    feedContent = getUQFeed(PARKINGLOTINFO)
    print(feedContent)


if __name__ == '__main__':
    main()
