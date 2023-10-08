import os

from twilio.rest import Client


def send_sms_notifications(users):
    for user in users:
        try:
            # Initialize Twilio client
            client = Client(os.getenv("TWILIO_ACCOUNT_SID"),
                            os.getenv("TWILIO_AUTH_TOKEN"))  # Replace with your Twilio credentials

            # Compose the SMS message
            message = client.messages.create(
                body=f"Connect to the WiFi using Username: {user.email} and Password: {user.password}, thank you",
                from_=os.getenv("YOUR_TWILIO_PHONE_NUMBER"),  # Replace with your Twilio phone number
                to=user.telephone_number
            )

            # Update sms_delivered based on Twilio response
            if message.status == "delivered":
                print(f"{'STATUS:SUCCESS'}:{message}")  # log success messages
                user.sms_delivered = True
            else:
                print(f"{'STATUS:FAILED'}:{message}")  # log failed messages
                user.sms_delivered = False
            user.save()

        except Exception as e:
            print(f"Error sending SMS to {user.email, ':', user.telephone_number}: {str(e)}")
