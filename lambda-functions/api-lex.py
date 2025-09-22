import json, os, time, boto3

lex = boto3.client("lexv2-runtime")
bedrock = boto3.client("bedrock-agent-runtime")  # if you use KB

def _resp(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(body)
    }

def lambda_handler(event, context):
    try:
        print("event:", event)
        body = event.get("body") or "{}"
        if isinstance(body, str):
            body = json.loads(body)
        message = body.get("message", "")
        user_id = body.get("userId") or f"user_{int(time.time()*1000)}"

        if not message:
            return _resp(400, {"error": "Missing 'message'."})

        # 1) Call Lex
        lex_resp = lex.recognize_text(
            botId=os.environ["BOT_ID"],
            botAliasId=os.environ["BOT_ALIAS_ID"],
            localeId=os.environ.get("BOT_LOCALE", "en_US"),
            sessionId=user_id,
            text=message
        )

        # Default reply
        msgs = lex_resp.get("messages", [])
        reply = " ".join([m.get("content", "") for m in msgs if m.get("content")]) or ""

        # 2) Return both plain reply & raw messages
        return _resp(200, {
            "reply": reply or "⚠️ No message",
            "raw": lex_resp  # ✅ expose full Lex response to frontend
        })

    except Exception as e:
        print("Error:", e)
        return _resp(500, {"error": str(e)})
