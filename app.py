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
import pycurl
import googlemaps

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)
 

@app.route('/webhook', methods=['POST'])
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
    if req.get("result").get("action") != "get_direction":
        return {}



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
    # res = makeWebhookResult(data)
    # print("666666:")
    # sys.stdout.flush()
    return res


def makeTranslateQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    japanese = parameters.get("japanese")
    if japanese is None:
        return None

    return japanese


def makeWebhookResult(data):
    query = data.get('data')
    if query is None:
        # return {}
        speech = "data is empty"

    result = query.get('translations')
    if result is None:
        # return {}
        speech = "translations is empty"

    translatedText = result.get('translatedText')
    if translatedText is None:
        # return {}
        speech = "translations text is empty"


    # print(json.dumps(item, indent=4))

    # speech = translatedText + " test"

    print("Response:")
    print(speech)
    sys.stdout.flush()

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "translate_japanese"
    }

    # return Response::json([
    #                 'speech'   => $speech,
    #                 'displayText' => $speech,
    #                 'data' => data,
    #                 'contextOut' => [],
    #                 'source' => "translate_japanese"
    #         ], 200);


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')