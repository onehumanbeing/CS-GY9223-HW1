import json
import boto3
import os
import traceback

sqs = boto3.client('sqs', region_name="us-east-1")
SQS_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/654654400451/CC_HW1_SQS"

def lambda_handler(event, context):
    try:
        print("Lex Event Received:", json.dumps(event, indent=2))
        
        # Check if this is a fulfillment request
        if event.get("invocationSource") != "FulfillmentCodeHook":
            return {
                "sessionState": {
                    "dialogAction": {
                        "type": "Delegate"
                    }
                }
            }
        
        slots = event["sessionState"]["intent"]["slots"]
        message = {
            "location": slots.get("Location", {}).get("value", {}).get("interpretedValue", ""),
            "cuisine": slots.get("Cuisine", {}).get("value", {}).get("interpretedValue", ""),
            "dining_time": slots.get("DiningTime", {}).get("value", {}).get("interpretedValue", ""),
            "number_of_people": slots.get("NumberOfPeople", {}).get("value", {}).get("interpretedValue", ""),
            "email": slots.get("Email", {}).get("value", {}).get("interpretedValue", "")
        }

        print("Extracted Parameters:", json.dumps(message, indent=2))

        response = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(message)
        )

        print("SQS Message ID:", response["MessageId"])
        return {
            "sessionState": {
                "dialogAction": {
                    "type": "Close",
                    "fulfillmentState": "Fulfilled"
                },
                "intent": {
                    "name": event["sessionState"]["intent"]["name"],
                    "slots": event["sessionState"]["intent"]["slots"],
                    "state": "Fulfilled"
                },
                "messages": [{
                    "contentType": "PlainText",
                    "content": "You're all set. Expect my suggestions shortly! Have a good day."
                }]
            }
        }

    except Exception as e:
        print("Error:", str(e))
        print(traceback.format_exc())
        return {
            "sessionState": {
                "dialogAction": {
                    "type": "Close",
                    "fulfillmentState": "Failed"
                },
                "messages": [{
                    "contentType": "PlainText",
                    "content": "Sorry, there was an error processing your request. Please try again."
                }]
            }
        }
