# This is the converter for crawler data to Elasticsearch import data

import json

index_name = "restaurants"


with open('manhattan_restaurants.json', 'r') as file:
    restaurants_data = json.load(file)

bulk_commands = []
for cuisine, restaurants in restaurants_data.items():
    for restaurant in restaurants:
        index_command = json.dumps({"index": {"_index": index_name, "_id": restaurant['id']}})
        doc_command = json.dumps({"RestaurantID": restaurant['id'], "Cuisine": cuisine})
        bulk_commands.extend([index_command, doc_command])

with open('bulk_commands.txt', 'w') as f:
    f.write('\n'.join(bulk_commands) + '\n') 

print("Bulk commands have been written to bulk_commands.txt")
