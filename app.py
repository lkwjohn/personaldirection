#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import sys
import googlemaps

from flask import Flask
from flask import request
from flask import make_response
from datetime import datetime

# Flask app should start in global layout
app = Flask(__name__)
 

# @app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


@app.route('/', methods=['GET', 'POST'])
def processRequest():

    print("2222:")
    sys.stdout.flush()

    gmaps = googlemaps.Client(key='AIzaSyAhF49eTdOK088ldtFFkqEGt50FzWXSVoc')

    print("3333:")
    sys.stdout.flush()


    make()

    print("66666:")
    sys.stdout.flush()


    print("77777:")
    print(res)
    sys.stdout.flush()
    return res

def make():
    url = 'http://maps.googleapis.com/maps/api/directions/json?%s' % urlencode((
            ('origin', 'jurong west central 3, singapore'),
            ('destination', 'city hall mrt, singapore'),
            ('mode', 'transit')
            ))

    googleResponse = urllib.urlopen(url)
    jsonResponse = json.loads(googleResponse.read())

    speech = ''
    for i in range (0, len (jsonResponse['routes'][0]['legs'][0]['steps'])):
        j = jsonResponse['routes'][0]['legs'][0]['steps'][i]['html_instructions']   
        speech += j + " "

    print(speech)
    sys.stdout.flush()


    # directions_result = gmaps.directions("Jurong point, singapore",
    #                                      "City Hall, singapore",
    #                                      mode="transit")

    # return directions_result


def makeTranslateQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    japanese = parameters.get("japanese")
    if japanese is None:
        return None

    return japanese


def makeWebhookResult(data):

    speech = " test"

    print("Response:")
    print(speech)
    sys.stdout.flush()

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "google_map"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')