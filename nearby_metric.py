import json
import requests
from pymongo import MongoClient
import time

client = MongoClient("localhost", 27017)
db = client.geocoder
collection = db.geolatlng

all_ids = list(collection.find({}, {"_id": 1, "lat": 1, "lang": 1}).sort("_id", 1).skip(1)) # skipping the header


def get_count(lat_lng_string, type, radius, key, key_req_count):
    # gives number of places of type type on radius of radius meters
    try:
        count = 0
        nearby_lat_lng = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+lat_lng_string+'&radius='+radius+'&types='+type+'&key='+key)
        key_req_count[0] += 1
        nearby_lat_lng_json = nearby_lat_lng.json()
        print "Request Count", key_req_count[0], nearby_lat_lng_json["status"]
        count += len(nearby_lat_lng_json["results"])

        while nearby_lat_lng_json.has_key("next_page_token"):
            next_page_token = nearby_lat_lng_json["next_page_token"]
            time.sleep(2)
            nearby_lat_lng = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='+lat_lng_string+'&radius='+radius+'&type='+type+'&pagetoken='+next_page_token+'&key='+key)
            key_req_count[0] += 1
            nearby_lat_lng_json = nearby_lat_lng.json()
            print "Request Count", key_req_count[0], nearby_lat_lng_json["status"]
            count += len(nearby_lat_lng_json["results"])

        return count
    except Exception as e:
        print e

def nearby_features(id,lat_lng_string,types, key_req_count, api_key):
    # gives number of places of all types and stores them in database
    try:
        result = {}
        radius = str(1000)
        for type in types:
            if key_req_count[0] > 975:
                api_key = get_new_key(key_index[0])
                key_req_count[0] = 0
            result[type] = get_count(lat_lng_string,type, radius, api_key, key_req_count)
            print " Total Requests Done =>", key_req_count[0]
        collection.update({"_id": id}, {'$set':{"locality": result}},upsert=False, multi=True)

    except Exception as e:
        print e

def get_locality_metric(score_dict):
    # calculates locality quality metric
    score = 0
    for k in score_dict.keys():
        score += score_dict[k]
    return score/60.0

def add_locality_metric(id):
    # Adds locality quality metric to the location.
    locl = list(collection.find({"_id": id},{"locality":1}))
    if locl[0].has_key("locality"):
        locality_ix = dict(locl[0]["locality"])
        collection.update({"_id": id}, {'$set':{"locality_metric": round(get_locality_metric(locality_ix),2)}}, upsert=False, multi=True)

keys = [] # Plug array of api keys
key_req_count = [0]
key_index = [0]
api_key = keys[key_index[0]]

def get_new_key(key_index):
    # Plugs out almost exhausted keys
    if key_index < len(keys)-1:
        key_index += 1
        api_key = keys[key_index[0]]
    return api_key

types = ["atm", "bus_station", "food", "hospital" ,"shopping_mall"] # types of amenties on which a locality is getting judged

for obj in all_ids:
    lat_lng_string = obj["lat"] +","+ obj["lang"]
    nearby_features(obj["_id"], lat_lng_string, types, key_req_count, api_key)
    add_locality_metric(obj["_id"])
