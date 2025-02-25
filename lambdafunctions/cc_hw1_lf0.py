import json
import boto3
import os
import traceback

# Lex V2 Bot and Alias IDs
LEX_BOT_ID = "WY3X0QOPJN"  
LEX_BOT_ALIAS_ID = "TSTALIASID"  
AWS_REGION = "us-east-1"

# Initialize Lex client
lex_client = boto3.client("lexv2-runtime", region_name=AWS_REGION)

def lambda_handler(event, context):
    try:
        # Determine if request is coming from API Gateway or direct testing
        if "body" in event:
            body = json.loads(event["body"])  # If coming from API Gateway, parse body
        else:
            body = event  # If direct invocation, use event as body
        
        user_id = body.get("userId", "default_user")  # Default user ID if not provided

        # Extract 'messages' array from request
        messages = body.get("messages", [])
        if not messages or not isinstance(messages, list):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid request format"})
            }
        
        # Get text from the first message
        text_message = messages[0].get("unstructured", {}).get("text", "")

        if not text_message:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Message cannot be empty"})
            }

        # Send message to Amazon Lex V2 (using correct IDs)
        lex_response = lex_client.recognize_text(
            botId=LEX_BOT_ID,          
            botAliasId=LEX_BOT_ALIAS_ID, 
            localeId="en_US",          # Language setting
            sessionId=user_id,         # Maintain conversation state per user
            text=text_message
        )

        # Extract Lex response messages
        lex_messages = lex_response.get("messages", [])

        # Format response for frontend
        formatted_messages = []
        for msg in lex_messages:
            formatted_messages.append({
                "type": "unstructured",
                "unstructured": {"text": msg["content"]}
            })

        return {
            "messages": formatted_messages
        }

    except Exception as e:
        return {
            "messages": [{
                "type": "unstructured",
                "unstructured": {"text": f"Error processing your request: {str(e)}"}
            }],
            "error": traceback.format_exc()
        }
