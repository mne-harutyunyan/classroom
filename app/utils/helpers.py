import httpx
from functools import wraps
from quart import request, jsonify

from app.config.settings import settings

def admin_required(func):
  @wraps(func)
  async def wrapper(*args, **kwargs):
    user_role = request.headers.get("Role")
    if user_role != "admin":
      return jsonify({"error": "Admin access required"}), 403 
    return await func(*args, **kwargs)
  return wrapper

async def send_slack_notification(message: str, reservation_id: str):
  if settings.SLACK_WEBHOOK_URL:
    payload = {
      "text": message,
      "attachments": [
        {
          "text": "Do you approve this reservation?",
          "fallback": "You are unable to approve the reservation",
          "callback_id": reservation_id,
          "actions": [
            {
              "name": "approve",
              "text": "Approve",
              "type": "button",
              "value": "approve"
            },
            {
              "name": "reject",
              "text": "Reject",
              "type": "button",
              "value": "reject"
            }
          ]
        }
      ]
    }
    async with httpx.AsyncClient() as client:
      response = await client.post(settings.SLACK_WEBHOOK_URL, json=payload)
      print(f"Status Code: {response.status_code}")
      print(f"Response Text: {response.text}")
      return response.status_code == 200, response.text
  else:
    raise ValueError("Slack webhook URL is not configured.")
