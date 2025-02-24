# This is the crawler for Yelp API

import requests
import time
import json
import os

API_KEY = os.getenv("YELP_API_KEY")
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
BASE_URL = "https://api.yelp.com/v3/businesses/search"

CUISINES = ["Chinese", "Italian", "Indian"]
LOCATION = "Manhattan, NY"
RESULTS_PER_CUISINE = 50  # each cuisine get 50 restaurants
MAX_RESULTS_PER_REQUEST = 25  # Yelp API limit 25 restaurants per request
RESTAURANTS = {}

# iterate over different cuisines to get data
for cuisine in CUISINES:
    print(f"Fetching restaurants for cuisine: {cuisine}")
    fetched_restaurants = set()
    restaurants_list = []
    
    for offset in range(0, RESULTS_PER_CUISINE, MAX_RESULTS_PER_REQUEST):
        params = {
            "term": f"{cuisine} restaurant",
            "location": LOCATION,
            "limit": MAX_RESULTS_PER_REQUEST,
            "offset": offset
        }

        response = requests.get(BASE_URL, headers=HEADERS, params=params)
        data = response.json()
        
        if "businesses" not in data:
            print(f"Error fetching {cuisine} restaurants: {data}")
            break
        
        for restaurant in data["businesses"]:
            if restaurant["id"] not in fetched_restaurants:
                fetched_restaurants.add(restaurant["id"])
                restaurants_list.append({
                    "id": restaurant["id"],
                    "name": restaurant["name"],
                    "cuisine": cuisine,
                    "rating": restaurant.get("rating", None),
                    "review_count": restaurant.get("review_count", None),
                    "address": ", ".join(restaurant["location"].get("display_address", [])),
                    "latitude": restaurant["coordinates"].get("latitude", None),
                    "longitude": restaurant["coordinates"].get("longitude", None),
                    "phone": restaurant.get("display_phone", None),
                    "url": restaurant.get("url", None),
                })
        # control API rate to avoid being rate limited
        time.sleep(1)

    RESTAURANTS[cuisine] = restaurants_list
    print(f"✅ Retrieved {len(restaurants_list)} {cuisine} restaurants.")

# save data to JSON file
with open("manhattan_restaurants.json", "w", encoding="utf-8") as f:
    json.dump(RESTAURANTS, f, indent=4, ensure_ascii=False)

print("✅ Data collection complete! Saved as manhattan_restaurants.json")
