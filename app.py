#!/usr/bin/env python

from __future__ import print_function
# from future.standard_library import install_aliases
# install_aliases()

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

    # # Geocoding an address
    # geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

    # print("4444:")
    # sys.stdout.flush()

    # # Look up an address with reverse geocoding
    # reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

    # print("5555:")
    # sys.stdout.flush()

    # Request directions via public transit

    directions_result = gmaps.directions("Jurong point, singapore",
                                         "City Hall, singapore",
                                         mode="transit")

    print("66666:")
    sys.stdout.flush()


    # baseurl = "https://translation.googleapis.com/language/translate/v2?key=AIzaSyAhF49eTdOK088ldtFFkqEGt50FzWXSVoc&source=jp&target=en&"
    # translate_query = makeTranslateQuery(req)

    # print("2222:")
    # sys.stdout.flush()
    # if translate_query is None:
    #     return {}
    # yql_url = baseurl + urlencode({'q': translate_query}) 

    # print("333333:")
    # sys.stdout.flush()
    # result = urlopen(yql_url).read()

    # print("444444:")
    # sys.stdout.flush()
    # data = json.loads(result)

    # print("55555:")
    # sys.stdout.flush()
    res = makeWebhookResult(directions_result)
    # print("666666:")
    # sys.stdout.flush()

    print("77777:")
    print(res)
    sys.stdout.flush()
    return res


def makeTranslateQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    japanese = parameters.get("japanese")
    if japanese is None:
        return None

    return japanese


def makeWebhookResult(data):
    # query = data.get('data')
    # if query is None:
    #     # return {}
    #     speech = "data is empty"

    # result = query.get('translations')
    # if result is None:
    #     # return {}
    #     speech = "translations is empty"

    # translatedText = result.get('translatedText')
    # if translatedText is None:
    #     # return {}
    #     speech = "translations text is empty"


    # print(json.dumps(item, indent=4))

    # speech = translatedText + " test"

    print("Response:")
    print(speech)
    sys.stdout.flush()

    return {
        "speech": data,
        "displayText": dat,
        # "data": data,
        # "contextOut": [],
        "source": "google_map"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')