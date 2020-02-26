from uq_feed_helper import *
from flask import Flask, request
from flask_restful import Resource, Api
from flask_jsonpify import jsonpify
from middleware import *
from waitress import serve
import sys
import json


app = Flask(__name__)
api = Api(app)


print("----------------------------------")
print("Loading Parking Lot Info...")
f = open("ParkingAddressMapper.json", "r")
PARKINGLOTINFO = json.loads(f.read())
f.close()
print("Loaded!")
print("----------------------------------")
print("----------------------------------")
print("Loading Config File...")
c = open('config.json')
WAITRESS = json.loads(c.read())
print("Config File Loaded.")
print("----------------------------------")


class getRealTimeStatus(Resource):
    def get(self):
        lot = request.args["lot"] if "lot" in request.args else ""
        lotType = request.args["type"] if "type" in request.args else ""
        feedContent = getUQFeed(PARKINGLOTINFO, lot, lotType)
        return jsonpify(feedContent)


api.add_resource(getRealTimeStatus, "/status")


if __name__ == '__main__':
    arguments = sys.argv
    if len(arguments) == 1:
        app.config["DEBUG"] = True
        print("App run in dev mode on port: ", WAITRESS["port"])
        app.run(port=WAITRESS["port"])
    elif len(arguments) == 2 and (arguments[1] == "--dev" or arguments[1] == "-d"):
        app.config["DEBUG"] = True
        print("App run in dev mode on port: ", WAITRESS["port"])
        app.run(port=WAITRESS["port"])
    elif len(arguments) == 2 and (arguments[1] == "--prod" or arguments[1] == "-p"):
        serve(
            app,
            host=WAITRESS["host"],
            port=WAITRESS["port"],
            ipv4=WAITRESS["ipv4"],
            ipv6=WAITRESS["ipv6"],
            threads=WAITRESS["threads"],
            url_scheme=WAITRESS["url_scheme"]
        )
    else:
        print("Wrong arguments, please check your input.")
