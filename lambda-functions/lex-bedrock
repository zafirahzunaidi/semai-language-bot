import json
import boto3
import re

# Initialize clients outside handler for reuse
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    print("Received event")
    
    try:
        user_message = event['inputTranscript']
        intent_name = event['sessionState']['intent']['name']
        knowledge_base_id = 'VHSLG3HIGZ'
        
        if intent_name != 'FallbackIntent':
            return {
                "sessionState": {
                    "dialogAction": {"type": "Close"},
                    "intent": {"name": intent_name, "state": "Fulfilled"}
                },
                "messages": [{"contentType": "PlainText", "content": "I can only help with translation requests."}]
            }

        # Step 1: Retrieve from Knowledge Base
        print("Retrieving from knowledge base...")
        retrieval_response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=knowledge_base_id,
            retrievalQuery={'text': user_message},
            retrievalConfiguration={'vectorSearchConfiguration': {'numberOfResults': 3}}
        )
        
        if not retrieval_response['retrievalResults']:
            return {
                "sessionState": {
                    "dialogAction": {"type": "Close"},
                    "intent": {"name": intent_name, "state": "Fulfilled"}
                },
                "messages": [{"contentType": "PlainText", "content": "Sorry, no information found about that translation."}]
            }

        # Build context
        context = "\n\n".join(result['content']['text'] for result in retrieval_response['retrievalResults'])
        
        # Step 2: Invoke Nova Pro model with a more specific prompt
        print("Invoking Nova Pro model...")
        prompt = f"""Based on this context:
{context}

User question: {user_message}

Provide ONLY the direct answer from the context. Do not add explanations, formatting, or additional text. Just give the exact translation or information as it appears in the context.

Answer:"""

        invoke_response = bedrock_runtime.invoke_model(
            modelId='amazon.nova-pro-v1:0',
            body=json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}]
            }),
            contentType='application/json',
            accept='application/json'
        )

        response_body = json.loads(invoke_response['body'].read())
        bot_response = response_body['output']['message']['content'][0]['text']

        # Clean up the response - remove any markdown formatting or extra spaces
        bot_response = re.sub(r'\*\*|\*|#+', '', bot_response).strip()
        bot_response = re.sub(r'\n+', ' ', bot_response).strip()

        # Prepare response
        messages = [{"contentType": "PlainText", "content": bot_response}]

        return {
            "sessionState": {
                "dialogAction": {"type": "Close"},
                "intent": {"name": intent_name, "state": "Fulfilled"}
            },
            "messages": messages
        }

    except Exception as e:
        print(f"Error in Lambda handler: {str(e)}")
        return {
            "sessionState": {
                "dialogAction": {"type": "Close"},
                "intent": {"name": "FallbackIntent", "state": "Fulfilled"}
            },
            "messages": [{"contentType": "PlainText", "content": "I'm experiencing technical difficulties. Please try again."}]
        }
