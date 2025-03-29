from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from notion_status_trigger import update_status
import hmac
import hashlib

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Verify Slack webhook secret
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

class SlackMessage(BaseModel):
    text: str

async def verify_slack_request(request: Request, x_slack_signature: str = Header(None)):
    if not SLACK_SIGNING_SECRET:
        return True  # Skip verification if secret not configured

    if not x_slack_signature:
        return False

    body = await request.body()
    timestamp = x_slack_signature.split('=')[0]
    signature = x_slack_signature.split('=')[1]

    sig_basestring = f"v0:{timestamp}:{body.decode()}"
    my_signature = hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, my_signature)

@app.options("/webhook")
async def options_webhook():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-Slack-Signature"
        }
    )

@app.post("/webhook")
async def handle_webhook(request: Request, x_slack_signature: str = Header(None)):
    # Verify the request is coming from Slack
    if not await verify_slack_request(request, x_slack_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Get the request data
    data = await request.json()

    # Extract relevant information from the Slack message
    try:
        # Example: expecting message in format "update status for <task_name> to <new_status> [github_url]"
        message = data.get('text', '')
        if not message.startswith('update status for'):
            raise HTTPException(status_code=400, detail="Invalid message format")

        # Parse the message
        parts = message.split()
        if len(parts) < 6:
            raise HTTPException(status_code=400, detail="Message missing required parts")

        task_name = parts[3]
        new_status = parts[5]
        github_url = parts[6] if len(parts) > 6 else None

        # Update the Notion status
        success = update_status(task_name, headers, new_status, github_url)

        if success:
            return {"message": "Status updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update status")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))