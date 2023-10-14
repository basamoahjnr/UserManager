import os
from logging import getLogger

from apscheduler.schedulers.background import BackgroundScheduler
from django.db import transaction
from twilio.rest import Client

from .mikrotik import get_hotspot_profiles
from .models import UserInfo, RadCheck, RadGroupCheck, RadUserGroup, RadGroupReply

scheduler = BackgroundScheduler()
logger = getLogger(__name__)


@transaction.atomic
def process_enabled_users():
    """Processes enabled users: creates RADIUS user accounts, groups, and sends SMS notifications."""
    try:
        enabled_users = UserInfo.objects.filter(is_enabled=True, sms_delivered=False).order_by('-updated_at')[:10]

        for user in enabled_users:

            if not user.email or not user.portalloginpassword or not user.profile:
                logger.error(f"Error processing user {user.email}: Missing required parameters")
                continue
            # create the user
            RadCheck.objects.get_or_create(username=user.email,
                                           attribute='Cleartext-Password',
                                           value=user.portalloginpassword,
                                           op=':=')
            # set the users group
            RadUserGroup.objects.get_or_create(username=user.email,
                                               groupname=user.profile,
                                               priority=1)
            # set the reply attribute for this user
            RadGroupReply.objects.get_or_create(groupname=user.profile,
                                                attribute='Mikrotik-Group',
                                                op=':=',
                                                value=user.profile)

            try:
                sid = send_sms_notification(user)
                if sid:
                    logger.info(f"SMS sent successfully to {user.email}")
                    user.smsdelivered = True
                    user.twilio_sid = sid
                    user.username = user.email
                    user.save()  # Update the sms_delivered flag here
                else:
                    logger.error(f"SMS delivery failed for {user.email}")

            except Exception as e:
                logger.error(f"Error processing user with {user.email}: {user.mobilephone.as_e164} : {str(e)}")

    except Exception as e:
        logger.error(f"Error processing enabled users: {str(e)}")


def send_sms_notification(user):
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    message = client.messages.create(
        body=f"Connect to the WiFi using \n"
             f"username: {user.email} with this"
             f"password: {user.portalloginpassword}\n"
             f"Thank You",
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=user.mobilephone.as_e164
    )
    return message.sid


def radgroupcheck():
    groups_to_create = get_hotspot_profiles(os.getenv('M_IP'), os.getenv('M_USERNAME'), os.getenv('M_PASSWORD'))
    for group in groups_to_create:
        RadGroupCheck.objects.get_or_create(groupname=group, attribute='Mikrotik-Group', op=':=', value=group)


# Schedule the process_enabled_users() function to run every 5 seconds
scheduler.add_job(radgroupcheck, 'interval', seconds=60 * 15, max_instances=1)
scheduler.add_job(process_enabled_users, 'interval', seconds=60 * 30)

# Start the scheduler only if it's not already running
if not scheduler.running:
    scheduler.start()
