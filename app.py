#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from HTMLParser import HTMLParser

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

    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)



    result = req.get("result")
    action = result.get("action")
    parameters = result.get("parameters")

    print("aaaaaa")
    sys.stdout.flush()
    if action == 'ask_direction':
        print("bbbbbb")
        sys.stdout.flush()
        return askDirection(parameters)
    elif action == 'ask_travel_time':
        print("cccccc")
        sys.stdout.flush()
        return askTime(parameters)

    print("dddddd")
    sys.stdout.flush()
    
    
    

def askTime(parameters):
    origin = parameters.get("origin")
    destination = parameters.get("destination")

    speech = ''
    for i in range (0,2):
        mode = ''
        if i == 0:
            mode = 'driving'
        else:
            mode = 'transit'

        baseurl = 'https://maps.googleapis.com/maps/api/directions/json?%s&key=AIzaSyAhF49eTdOK088ldtFFkqEGt50FzWXSVoc' % urlencode((
                ('origin', origin + ", singapore"),
                ('destination', destination + ", singapore"),
                ('mode', mode)
                )) 
        print("zzzzzzz: " + baseurl)
        sys.stdout.flush()
        googleResponse =  urlopen(baseurl).read()

        jsonResponse = json.loads(googleResponse)

        print("xxxxxx")
        sys.stdout.flush()

        total_time = jsonResponse['routes'][0]['legs'][0]['duration']['text']
        speech += "Total time by " + mode + " is " + total_time + ". "
            
    return makeWebhookResult(speech)



def askDirection(parameters):

    origin = parameters.get("origin")
    if origin is None:
        return makeWebhookResult('Hmmm, you are coming from?')

    destination = parameters.get("destination")
    if destination is None:
        return makeWebhookResult('Okay, i got where you are coming from, but where are you going to?')

    transport_mode  = parameters.get("transport")
    transit_mode    = parameters.get("transit_mode")

    if (transport_mode is None or transport_mode == '') and (transit_mode is None or transit_mode == ''): #did not supply transport mode
        return makeWebhookQuestion(origin, destination)
    elif (transport_mode is None or transport_mode == '') and (transit_mode is not None or transit_mode != ''):
        if transit_mode == 'bus' or transit_mode == 'train' or transit_mode == 'subway':
            transport_mode = 'transit' #default


    print(origin + "| |" + destination + "| |" + transport_mode + "| |" + transit_mode)
    sys.stdout.flush()

    baseurl = 'https://maps.googleapis.com/maps/api/directions/json?%s&key=AIzaSyAhF49eTdOK088ldtFFkqEGt50FzWXSVoc' % urlencode((
            ('origin', origin + ", singapore"),
            ('destination', destination + ", singapore"),
            ('mode', transport_mode),
            ('transit_mode', transit_mode)
            )) 

    googleResponse =  urlopen(baseurl).read()

    jsonResponse = json.loads(googleResponse)

    speech = ''
    second = 0

    

    if(len(jsonResponse['routes']) > 0 and len(jsonResponse['routes'][0]['legs']) > 0):
        numberOfRoute = len(jsonResponse['routes']);

        #get total distance
        distance = jsonResponse['routes'][0]['legs'][0]['distance']['text']
        distance_speech = "Total distance is " + distance + ". "
        speech = ""

        length = len (jsonResponse['routes'][0]['legs'][0]['steps'])
        #loop through the steps to get to the destination
        for i in range (0, len (jsonResponse['routes'][0]['legs'][0]['steps'])):
            j = "" #clear out
            
            j = jsonResponse['routes'][0]['legs'][0]['steps'][i]['html_instructions'] 
            htmlExtractor = MLStripper()
            htmlExtractor.feed(j)
            j = htmlExtractor.get_data()

            try:
                method = jsonResponse['routes'][0]['legs'][0]['steps'][i]['travel_mode']
                if method == 'TRANSIT':
                    departure_stop = jsonResponse['routes'][0]['legs'][0]['steps'][i]['transit_details']['departure_stop']['name']
                    arrival_stop = jsonResponse['routes'][0]['legs'][0]['steps'][i]['transit_details']['arrival_stop']['name']
                    vehicle_type = jsonResponse['routes'][0]['legs'][0]['steps'][i]['transit_details']['line']['vehicle']['name']

                    if vehicle_type.lower() == 'bus':
                        transport = jsonResponse['routes'][0]['legs'][0]['steps'][i]['transit_details']['line']['short_name']
                        j = "Board " + vehicle_type + " number " + transport + " from " + departure_stop + " to " + arrival_stop
                    else: #subway
                        transport = jsonResponse['routes'][0]['legs'][0]['steps'][i]['transit_details']['line']['name']
                        j = "Take "+ transport + " from " + departure_stop + " to " + arrival_stop

            except Exception as e: 
                pass #for driving/walking

            if(i == 0):
                speech = j + " "
            else:
                if(i == length - 1):
                    speech +=  j #EOL
                else:
                    speech += j + ". Next, "

    else:
        speech = "I could not find any route from " + origin + " to " + destination

    speech = distance_speech + speech

    print("url:" + baseurl)
    sys.stdout.flush()

    return makeWebhookResult(speech)

#if the user didn't provide the transport mode
def makeWebhookQuestion(origin, destination):

    return {
        "followupEvent": {
              "name": "ask_transport_event",
              "data": {
                 "origin": origin , "destination": destination
              }
           }
    }


def makeWebhookResult(data):

    return {
        "speech": data,
        "displayText": "Here's the result",

        "source": "google_map"
    }

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')