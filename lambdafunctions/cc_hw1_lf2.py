import json
import boto3
import random
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import traceback

sqs = boto3.client("sqs", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
ses = boto3.client("ses", region_name="us-east-1")

ES_HOST = "https://search-restaurants-ju42e5gpz2jqanbrpz7kcdtnrm.us-east-1.es.amazonaws.com"
INDEX_NAME = "restaurants"

SQS_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/654654400451/CC_HW1_SQS"
DYNAMODB_TABLE_NAME = "yelp-restaurants"
SENDER_EMAIL = "no-reply@thecertified.xyz"

# Add AWS authentication for Elasticsearch
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    'us-east-1',
    'es',
    session_token=credentials.token
)

es = OpenSearch(
    hosts=[ES_HOST],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection,
    ssl_show_warn=False
)

def get_random_restaurant_from_es(cuisine):
    """Fetch a random restaurant from ElasticSearch for the given cuisine."""
    query = {
        "size": 10,
        "query": {
            "match": {
                "Cuisine": {
                    "query": cuisine,
                    "operator": "and"
                }
            }
        }
    }
    response = es.search(index=INDEX_NAME, body=query)
    hits = response.get("hits", {}).get("hits", [])

    if not hits:
        return None  # No restaurants found

    return random.choice(hits)["_source"]["RestaurantID"]  # Pick a random one

def get_restaurant_details_from_dynamodb(restaurant_id):
    """Fetch restaurant details from DynamoDB."""
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    response = table.get_item(Key={"business_id": restaurant_id})
    
    return response.get("Item", None)

def send_email(to_email, subject, body):
    """Send email using AWS SES."""
    response = ses.send_email(
        Source=SENDER_EMAIL,
        Destination={"ToAddresses": [to_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": body}},
        },
    )
    return response

def lambda_handler(event, context):
    """Lambda function to process SQS messages, fetch recommendations, and send emails."""
    try:
        # SQS trigger sends records in event
        for record in event['Records']:
            body = json.loads(record['body'])

            cuisine = body.get("cuisine", "")
            email = body.get("email", "")

            if not cuisine or not email:
                print("Missing required fields in SQS message.")
                return

            restaurant_id = get_random_restaurant_from_es(cuisine)
            if not restaurant_id:
                print(f"No restaurant found for cuisine: {cuisine}")
                return
            
            restaurant_details = get_restaurant_details_from_dynamodb(restaurant_id)
            if not restaurant_details:
                print(f"No details found for restaurant ID: {restaurant_id}")
                return

            restaurant_name = restaurant_details.get("name", "Unknown Restaurant")
            address = restaurant_details.get("address", "Address not available")
            rating = restaurant_details.get("rating", "N/A")
            review_count = restaurant_details.get("review_count", "N/A")

            email_subject = f"Your {cuisine} Restaurant Recommendation!"
            email_body = (
                f"Hello,\n\nHere is a {cuisine} restaurant recommendation for you:\n\n"
                f"🍽️ {restaurant_name}\n"
                f"📍 Address: {address}\n"
                f"⭐ Rating: {rating} (based on {review_count} reviews)\n\n"
                "Enjoy your meal!\n\nBest,\nYour Restaurant Recommendation Bot"
            )
            send_email(email, email_subject, email_body)
            print(f"Email sent to {email} with recommendation.")

    except Exception as e:
        print(f"Error processing SQS message: {str(e)}")
        print(traceback.format_exc())