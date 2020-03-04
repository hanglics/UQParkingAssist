import json
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from flask_jsonpify import jsonpify
from flask_restful import Resource, Api
from waitress import serve

from uq_feed_helper import *
from ERRORS import *

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
CONFIG = json.loads(c.read())
print("Config File Loaded.")
print("----------------------------------")


# loc and userType are required
class getRealTimeStatus(Resource):
    def get(self):
        lot = request.args["lot"] if "lot" in request.args else ""
        if "loc" in request.args:
            location = request.args["loc"]
        else:
            return jsonpify(MISSING_QUERY_PARAMETER_ERROR)
        if "userType" in request.args:
            userType = request.args["userType"]
        else:
            return jsonpify(MISSING_QUERY_PARAMETER_ERROR)
        feedContent = getResponse(PARKINGLOTINFO, lot, location, CONFIG, userType)
        if len(feedContent) == 0:
            return jsonpify(NO_PARKING_AVAILABLE)
        res = jsonpify(feedContent)
        res.status_code = 200
        return res


api.add_resource(getRealTimeStatus, "/status")


if __name__ == '__main__':
    arguments = sys.argv
    if len(arguments) == 1:
        app.config["DEBUG"] = True
        print("App run in dev mode on port: ", CONFIG["port"])
        getUQFeed()
        app.run(port=CONFIG["port"])
    elif len(arguments) == 2 and (arguments[1] == "--dev" or arguments[1] == "-d"):
        app.config["DEBUG"] = True
        print("App run in dev mode on port: ", CONFIG["port"])
        getUQFeed()
        app.run(port=CONFIG["port"])
    elif len(arguments) == 2 and (arguments[1] == "--prod" or arguments[1] == "-p"):
        getUQFeed()
        serve(
            app,
            host=CONFIG["host"],
            port=CONFIG["port"],
            ipv4=CONFIG["ipv4"],
            ipv6=CONFIG["ipv6"],
            threads=CONFIG["threads"],
            url_scheme=CONFIG["url_scheme"]
        )
    else:
        print("Wrong arguments, please check your input.")
