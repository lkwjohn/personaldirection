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
    if origin is None:
        return makeWebhookResult('Hmmm, you are coming from?')

    destination = parameters.get("destination")
    if destination is None:
        return makeWebhookResult('Okay, i got where you are coming from, but where are you going to?')

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

        googleResponse =  urlopen(baseurl).read()

        jsonResponse = json.loads(googleResponse)

        seconds = 0

        if(len(jsonResponse['routes']) > 0 and len(jsonResponse['routes'][0]['legs']) > 0):
            for i in range (0, len (jsonResponse['routes'][0]['legs'][0]['steps'])):
                seconds += jsonResponse['routes'][0]['legs'][0]['steps'][i]['duration']['value']

            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)

            total_time = ''

            if h > 0:
                total_time += str(h) + " hours "

            if m > 0:
                total_time += str(m) + " mintues "

            total_time += str(s) + " seconds"


            speech += "Total time by " + mode + " is " + total_time + ". "
            

    
    return makeWebhookResult(speech)



def askDirection(parameters):
    
    print("1111111")
    sys.stdout.flush()

    origin = parameters.get("origin")
    if origin is None:
        return makeWebhookResult('Hmmm, you are coming from?')

    destination = parameters.get("destination")
    if destination is None:
        return makeWebhookResult('Okay, i got where you are coming from, but where are you going to?')

    transport_mode = parameters.get("transport")
    transit_mode = parameters.get("transit_mode")

    print(origin + "| |" + destination + "| >>>>>>>")
    sys.stdout.flush()

    if (transport_mode is None or transport_mode == '') and (transit_mode is  None or transit_mode == ''):
        print("| 33333333")
        sys.stdout.flush()
        return makeWebhookQuestion(origin, destination)
    elif (transport_mode is None or transport_mode == '') and (transit_mode is not None or transit_mode != ''):
        if transit_mode == 'bus' or transit_mode == 'train' or transit_mode == 'subway':
            transport_mode = 'transit' #default
    # elif mode == 'transit':
    #     if transit_mode is None or transit_mode == 'any':
    #         transit_mode = '' #any


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

        # if numberOfRoute == 1:
        #     speech = "There is 1 route found. "
        # elif numberOfRoute == 0:
        #     return makeWebhookResult("There is no route found from " + origin + " to " + destination + " by " + mode)
        # else:
            # speech = "There are " + str(numberOfRoute) + " route found. "

        length =  len (jsonResponse['routes'][0]['legs'][0]['steps'])

        for i in range (0, len (jsonResponse['routes'][0]['legs'][0]['steps'])):
            j = ""
            print("Steps: " + str(i) + " >>>> "  +j)
            sys.stdout.flush()
            

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

                    print(j + " TYPE >>>>>>> " + vehicle_type)
                    sys.stdout.flush()

                    if vehicle_type == 'bus':
                        transport = jsonResponse['routes'][0]['legs'][0]['steps'][i]['transit_details']['line']['short_name']
                        j = "Board " + vehicle_type + " number " + transport + " from " + departure_stop + " to " + arrival_stop
                    else: #subway
                        transport = jsonResponse['routes'][0]['legs'][0]['steps'][i]['transit_details']['line']['name']
                        j = "Take "+ transport + " from " + departure_stop + " to " + arrival_stop

            except Exception as e: 
                print(">>>>>>> " + str(e))
                sys.stdout.flush()
                pass 

            if(i == 0):
                speech = j + " "
            else:
                if(i == length - 1):
                    speech = speech + " " +  j #EOL
                else:
                    speech = speech + " " + j + ". ::next:: "

            print("Step " + j)
            sys.stdout.flush()
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