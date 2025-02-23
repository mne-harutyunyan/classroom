from twilio.rest import Client
from app.config.settings import settings

client = Client(settings.Account_SID, settings.Auth_Token)

def send_sms(to_phone_number, message):
    from_phone_number = '+14708377805'

    try:
        message = client.messages.create(
            body=message,
            from_=from_phone_number,
            to=to_phone_number
        )
        print(f"Message sent! SID: {message.sid}")
    except Exception as e:
        print(f"Error: {e}")
