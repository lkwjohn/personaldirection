import sys
import json, urllib
from urllib import urlencode
import pprint

import googlemaps

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

url = 'http://maps.googleapis.com/maps/api/directions/json?%s' % urlencode((
            ('origin', 'jurong west central 3, singapore'),
            ('destination', 'city hall mrt, singapore'),
            ('mode', 'transit')
 ))

googleResponse = urllib.urlopen(url)
jsonResponse = json.loads(googleResponse.read())
pprint.pprint(jsonResponse)

for i in range (0, len (jsonResponse['routes'][0]['legs'][0]['steps'])):
    j = jsonResponse['routes'][0]['legs'][0]['steps'][i]['html_instructions'] 
    print j                           

