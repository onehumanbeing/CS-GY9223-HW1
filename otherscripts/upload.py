# This is the uploader for DynamoDB from crawler data

import boto3
import json
import time
from datetime import datetime
from decimal import Decimal

with open("manhattan_restaurants.json", "r", encoding="utf-8") as f:
    restaurant_data = json.load(f)

dynamodb = boto3.resource("dynamodb", region_name="us-east-1") 
table = dynamodb.Table("yelp-restaurants")

for cuisine, restaurants in restaurant_data.items():
    print(f"start storing {cuisine} data...")
    
    for restaurant in restaurants:
        item = {
            "business_id": restaurant["id"],  # use id as DynamoDB primary key
            "name": restaurant["name"],
            "address": restaurant["address"],
            "coordinates": {
                "latitude": Decimal(str(restaurant["latitude"])),
                "longitude": Decimal(str(restaurant["longitude"])),
            },
            "review_count": restaurant["review_count"],
            "rating": Decimal(str(restaurant["rating"])),
            "zip_code": restaurant["address"].split(",")[-1].strip() if "," in restaurant["address"] else "N/A",
            "insertedAtTimestamp": datetime.utcnow().isoformat()  # insert time
        }

        try:
            table.put_item(Item=item)
            print(f"✅ {restaurant['name']} has been stored in DynamoDB")
        except Exception as e:
            print(f"❌ Failed to store {restaurant['name']}, error: {e}")
    time.sleep(1)

print("✅ All restaurant data has been stored in DynamoDB")
