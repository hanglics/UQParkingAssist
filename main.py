import json
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from flask_jsonpify import jsonpify
from flask_restful import Resource, Api
from waitress import serve

from uq_feed_helper import *

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=getUQFeed, trigger="interval", seconds=60)
scheduler.start()

app = Flask(__name__)
api = Api(app)


print("----------------------------------")
print("Loading Parking Lot Info...")
f = open("ParkingAddressMapper.json", "r")
PARKINGLOTINFO = json.loads(f.read())
f.close()
print("Loaded!")
print("----------------------------------")
print("Loading Config File...")
c = open('config.json')
WAITRESS = json.loads(c.read())
print("Config File Loaded.")
print("----------------------------------")


class getRealTimeStatus(Resource):
    def get(self):
        lot = request.args["lot"] if "lot" in request.args else ""
        location = request.args["loc"]
        userType = request.args["userType"]
        feedContent = getResponse(PARKINGLOTINFO, lot, location, userType)
        return jsonpify(feedContent)


api.add_resource(getRealTimeStatus, "/status")


if __name__ == '__main__':
    arguments = sys.argv
    if len(arguments) == 1:
        app.config["DEBUG"] = True
        print("App run in dev mode on port: ", WAITRESS["port"])
        getUQFeed()
        app.run(port=WAITRESS["port"])
    elif len(arguments) == 2 and (arguments[1] == "--dev" or arguments[1] == "-d"):
        app.config["DEBUG"] = True
        print("App run in dev mode on port: ", WAITRESS["port"])
        getUQFeed()
        app.run(port=WAITRESS["port"])
    elif len(arguments) == 2 and (arguments[1] == "--prod" or arguments[1] == "-p"):
        getUQFeed()
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
