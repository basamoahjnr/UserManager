import os

from apscheduler.schedulers.background import BackgroundScheduler
from django.db import transaction
from twilio.rest import Client

from .models import Registration, RadCheck, RadGroupCheck, RadUserGroup, RadGroupReply

scheduler = BackgroundScheduler()


# @transaction.atomic
# def create_radius_users(enabled_users):
#     activated_users = []
#     try:
#         for user in enabled_users:
#             email = user.email
#             password = user.password
#             profile = user.profile
#
#             RadCheck.objects.get_or_create(username=email, attribute='Cleartext-Password', value=password, op=':=')
#
#             groups_to_create = ['vip', 'viip']
#             for group in groups_to_create:
#                 RadGroupCheck.objects.get_or_create(groupname=group, attribute='Mikrotik-Group', op=':=', value=profile)
#
#             RadUserGroup.objects.get_or_create(username=email, groupname='vip', priority=1)
#             RadUserGroup.objects.get_or_create(username=email, groupname='viip', priority=1)
#
#             RadGroupReply.objects.get_or_create(groupname='vip', attribute='Mikrotik-Group', op=':=',
#                                                 value='vip')
#             RadGroupReply.objects.get_or_create(groupname='viip', attribute='Mikrotik-Group', op=':=',
#                                                 value='vvip')
#
#             activated_users.append(user)
#
#         return activated_users
#     except Exception as e:
#         print(f"Error: {e}")
#         return activated_users

@transaction.atomic
def create_radius_user(enabled_user):
    try:
        email = enabled_user.email
        password = enabled_user.password
        profile = enabled_user.profile

        RadCheck.objects.get_or_create(username=email, attribute='Cleartext-Password', value=password, op=':=')

        groups_to_create = ['vip', 'viip']
        for group in groups_to_create:
            RadGroupCheck.objects.get_or_create(groupname=group, attribute='Mikrotik-Group', op=':=', value=profile)

        RadUserGroup.objects.get_or_create(username=email, groupname='vip', priority=1)
        RadUserGroup.objects.get_or_create(username=email, groupname='viip', priority=1)

        RadGroupReply.objects.get_or_create(groupname='vip', attribute='Mikrotik-Group', op=':=',
                                            value='vip')
        RadGroupReply.objects.get_or_create(groupname='viip', attribute='Mikrotik-Group', op=':=',
                                            value='vvip')

        return enabled_user
    except Exception as e:
        print(f"Error creating RADIUS user: {e}")
        return None


def send_sms_notifications(users):
    for user in users:
        try:
            client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
            message = client.messages.create(
                body=f"Connect to the WiFi using \n"
                     f"Username: {user.email}\n"
                     f"and Password: {user.password}\n"
                     f" thank you",
                from_=os.getenv("TWILIO_PHONE_NUMBER"),
                to=user.telephone_number.as_e164
            )

            if message.status == "sent":
                print(f"STATUS: SUCCESS - {message}")
                user.sms_delivered = True
                user.save()
            else:
                print(f"STATUS: FAILED - {message}")
                user.sms_delivered = False
                user.save()

        except Exception as e:
            print(f"Error sending SMS to {user.email, ':', user.telephone_number}: {str(e)}")


def handle():
    enabled_users = Registration.objects.filter(is_enabled=True, sms_delivered=False).order_by('-updated_at')[:10]
    print(enabled_users.values())
    created_users = []

    if enabled_users:
        for user in enabled_users:
            created_user = create_radius_user(user)
            if created_user:
                created_users.append(created_user)
        if created_users:
            send_sms_notifications(created_users)


# Schedule the handle() function to run every 5 seconds
scheduler.add_job(handle, 'interval', seconds=5)

# Start the scheduler only if it's not already running
if not scheduler.running:
    scheduler.start()
