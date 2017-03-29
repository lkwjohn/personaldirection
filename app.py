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
import logging
import googlemaps

from flask import Flask
from flask import request
from flask import make_response
from datetime import datetime

# Flask app should start in global layout
app = Flask(__name__)
 

@app.route('/webhook', methods=['GET', 'POST'])
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


def processRequest(req):

    print("2222:")
    sys.stdout.flush()


    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)

    result = req.get("result")
    parameters = result.get("parameters")
    origin = parameters.get("origin")
    if origin is None:
        return makeWebhookResult('Hmmm, you are coming from?')

    destination = parameters.get("destination")
    if destination is None:
        return makeWebhookResult('Okay, i got where you are coming from, but where are you going to?')

    mode = parameters.get("transport_mode")
    transit_mode = parameters.get("transit_mode")
    if mode is None :
        if transit_mode == 'bus' or transit_mode == 'train' or transit_mode == 'subway':
            mode = 'transit' #default
        else:
            return makeWebhookResult('How do you want to get there by?')
    

    if mode == 'transit':
        if transit_mode is None or transit_mode == 'any':
            transit_mode = '' #any



    print(origin + " " + destination + " " + mode + " " + transit_mode)
    sys.stdout.flush()

    baseurl = 'https://maps.googleapis.com/maps/api/directions/json?%s&key=AIzaSyAhF49eTdOK088ldtFFkqEGt50FzWXSVoc' % urlencode((
            ('origin', origin + ", singapore"),
            ('destination', destination + ", singapore"),
            ('mode', mode),
            ('transit_mode', transit_mode)
            )) 

    googleResponse =  urlopen(baseurl).read()

    jsonResponse = json.loads(googleResponse)

    speech = ''

    if(len(jsonResponse['routes']) > 0 and len(jsonResponse['routes'][0]['legs']) > 0):
        length =  len (jsonResponse['routes'][0]['legs'][0]['steps'])
        for i in range (0, len (jsonResponse['routes'][0]['legs'][0]['steps'])):
            j = jsonResponse['routes'][0]['legs'][0]['steps'][i]['html_instructions'] 
           
            print("3333:" + str(i) + " " + str(length))
            sys.stdout.flush()
            if(i == 0):
                speech += j + " "
            else:
                if(i == length - 1):
                    speech += j #EOL
                else:
                    speech += j + " ::next:: "
    else:
        speech = "I could not find any route from " + origin + " to " + destination

    print("3333:" + speech)
    sys.stdout.flush()
    
    return makeWebhookResult(speech)




def makeWebhookResult(data):

    return {
        "speech": data,
        "displayText": data,
        "source": "google_map"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')