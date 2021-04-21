import os
import json
import urllib.request
import xml.etree.ElementTree as ET


GAPI_URL = 'https://maps.googleapis.com/maps/api/geocode/json?'
GAPI_KEY = 'AIzaSyCwzpaZXAqf8_stD_cga4CAp6OhkQWUWmQ'

def waypoints(filename):
    with open(filename, 'rb') as fp:
        xml = fp.read()
        tree = ET.fromstring(xml.decode('utf-8'))
        for c in tree:
            if c.tag == 'wpt':
                yield c


os.makedirs('.cached', exist_ok=True)

with open('tw_p300.csv', 'w', encoding='utf-8') as fp:
    fp.write('Rank,Name,Ele. (m),Prom. (m),County / City,Township / District\n')
    for wpt in waypoints('tw_p300.gpx'):
        lat = float(wpt.get('lat'))
        lon = float(wpt.get('lon'))

        # Fetch address from Google Geocoding API
        latlng = '{},{}'.format(lat, lon)
        filename = os.path.join('.', '.cached', 'zh-tw_{}.json'.format(latlng))
        try:
            with open(filename, 'r') as fp_:
                address = json.load(fp_)
        except FileNotFoundError:
            with urllib.request.urlopen('{}language=zh-tw&latlng={}&key={}'.format(
                    GAPI_URL, latlng, GAPI_KEY)) as http_:
                address = json.loads(http_.read())
                with open(filename, 'w') as fp_:
                    json.dump(address, fp_)

        ele = int(wpt.find('ele').text)
        name = wpt.find('name').text
        cmt = wpt.find('cmt').text
        no, properties = cmt.split(':')
        no = int(no)
        properties = [p.split('=') for p in properties.split(',')]
        properties = {k:v for k, v in properties}

        # Extract zh_TW address
        properties['county'] = ''
        properties['township'] = ''
        for r_ in address['results']:
            for c_ in r_['address_components']:
                if c_['short_name'] and 'administrative_area_level_1' in c_['types']:
                    properties['county'] = c_['short_name']
                elif c_['short_name'] and 'administrative_area_level_2' in c_['types']:
                    properties['county'] = c_['short_name']
                elif c_['short_name'] and 'administrative_area_level_3' in c_['types']:
                    properties['township'] = c_['short_name']

        print(properties)
        fp.write('{},{},{},{},{},{}\n'.format(no, name, ele, 
            properties['prom'], properties['county'], properties['township']))
