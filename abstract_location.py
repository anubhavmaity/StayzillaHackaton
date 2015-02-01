import json
from pymongo import MongoClient
from bson import json_util

client = MongoClient("localhost", 27017)
db = client.geocoder
collection = db.geolatlng

for location in collection.find():
    try:
        print location["lat"]
        print location["lang"]
        #print json.dumps(location["data"], indent=4, sort_keys=True)
        location_data = location["data"]
        results = location_data["results"]
        #print json.dumps(results[0]["address_components"], indent=4, sort_keys=True)
        #print len(results)
        first_address_component = results[0]["address_components"]
        #abstract_loc_index =  len(first_address_component)/2 - 1;
        #print first_address_component[abstract_loc_index]
        for location in first_address_component:
            if "sublocality_level_1" in location["types"]:
                print location["long_name"]
                break
            elif "locality" in location["types"]:
                print location["long_name"]
    except Exception, e:
        print(e)

