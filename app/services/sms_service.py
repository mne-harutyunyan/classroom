from http import HTTPStatus

from twilio.rest import Client

from app.config.settings import settings

client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)


def send_sms(to_phone_number: str, message: str) -> None:
  """
  Send an SMS message using Twilio.

  Args:
    to_phone_number (str): The recipient's phone number.
    message (str): The message to send.
  """
  from_phone_number = settings.FROM_PHONE_NUMBER
  
  try:
    message = client.messages.create(
      body=message,
      from_=from_phone_number,
      to=to_phone_number)

  except Exception as e:
    return {"error": str(e), "status_code": HTTPStatus.INTERNAL_SERVER_ERROR}