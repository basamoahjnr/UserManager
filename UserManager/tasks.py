import os

from apscheduler.schedulers.background import BackgroundScheduler
from django.db import transaction
from twilio.rest import Client

from .models import Registration, RadCheck, RadGroupCheck, RadUserGroup, RadGroupReply

scheduler = BackgroundScheduler()


@transaction.atomic
def create_radius_users(enabled_users):
    activated_users = []
    try:
        for user in enabled_users:
            email = user.email
            password = user.password
            profile = user.profile

            RadCheck.objects.create(username=email, attribute='Cleartext-Password', value=password, op=':=')

            groups_to_create = ['vip', 'viip']
            for group in groups_to_create:
                RadGroupCheck.objects.get_or_create(groupname=group, attribute='Mikrotik-Group', op=':=', value=profile)

            RadUserGroup.objects.get_or_create(username=email, groupname='vip', priority=1)
            RadUserGroup.objects.get_or_create(username=email, groupname='viip', priority=1)

            RadGroupReply.objects.get_or_create(groupname='vip', attribute='Some-Attribute', op=':=',
                                                value='Some-Value')
            RadGroupReply.objects.get_or_create(groupname='viip', attribute='Some-Attribute', op=':=',
                                                value='Some-Value')

            activated_users.append(user)

        return activated_users
    except Exception as e:
        print(f"Error: {e}")
        return activated_users


def send_sms_notifications(users):
    for user in users:
        try:
            client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
            message = client.messages.create(
                body=f"Connect to the WiFi using Username: {user.email} and Password: {user.password}, thank you",
                from_=os.getenv("TWILIO_PHONE_NUMBER"),
                to=user.telephone_number
            )

            if message.status == "delivered":
                print(f"STATUS: SUCCESS - {message}")
                user.sms_delivered = True
            else:
                print(f"STATUS: FAILED - {message}")
                user.sms_delivered = False
            user.save()

        except Exception as e:
            print(f"Error sending SMS to {user.email, ':', user.telephone_number}: {str(e)}")


def handle():
    enabled_users = Registration.objects.filter(is_enabled=True)[:10]
    if enabled_users:
        created_users = create_radius_users(enabled_users)
        if created_users:
            send_sms_notifications(created_users)


# Schedule the handle() function to run every 5 seconds
scheduler.add_job(handle, 'interval', seconds=1800)

# Start the scheduler only if it's not already running
if not scheduler.running:
    scheduler.start()
