#created a file to extract json data using google maps reverse geocoding api and store it into mongodb
import csv
import requests
import json
from pymongo import MongoClient

client = MongoClient("localhost", 27017)
db = client.geocoder
collection = db.geolatlng

with open('hackathon_location_data.csv', 'rb') as csvfile:
    try:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        count = 4998
        rows = list(spamreader)
        for row in rows[4998:]:
            count = count + 1
            lat = row[0]
            lang = row[1]
            location = row[2]
            #Getting the json with geocoding api, parameters are latitude and longitude
            page_location = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng=" + lat +"," +lang + "&key=API_KEY")
            #page_nearby = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + lat+ "," +lang+"&radius=500&types=food&key=AIzaSyAnt3xDKoFwjlt_tU90A9jNprOTwT_S2nY")
            page_location_json = page_location.json()
            #page_nearby_json = page_nearby.json()
            #print page_json

            print json.dumps(page_location_json, indent=4, sort_keys=True)
            #print json.dumps(page_nearby_json, indent=4, sort_keys=True)
            if count == 5001:
                break

            post = {"lat":lat, "lang":lang, "data":page_location_json}
            post_id = collection.insert(post)
            
            print(count)


    except Exception, e:
        print(count)
        print(e)