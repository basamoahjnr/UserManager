import os
import time

from django.core.management.base import BaseCommand
from twilio.rest import Client

from UserManager.create_radius_users import create_radius_user
from UserManager.models import UserInfo


class Command(BaseCommand):
    help = 'Send SMS notifications to users'

    def add_arguments(self, parser):
        parser.add_argument('--date_range', help='Specify a date range in the format YYYY-MM-DD,YYYY-MM-DD')
        parser.add_argument('--group', help='Specify a group name')
        parser.add_argument('--sms_message', help='Specify a custom SMS message')

    def handle(self, *args, **options):
        date_range = options['date_range']
        group = options['group']
        sms_message = options['sms_message']

        # Fetch users who satisfy the specified conditions and have been enabled
        users = UserInfo.objects.filter(isenabled=True)
        if date_range:
            users = users.filter(created_at__range=date_range.split(','))
        if group:
            users = users.filter(groups__name=group)

        # Create RADIUS users for the users
        radius_users = []
        for user in users:
            u = create_radius_user(user)
            radius_users.append(u)

        # Send SMS notifications to the RADIUS users
        sms_client = Client(os.getenv("TWILIO_ACCOUNT_SID"),
                            os.getenv("TWILIO_AUTH_TOKEN"))
        for u in radius_users:
            sms_message = sms_message or f'Connect to the KKCR WiFi using Username:' \
                                         f' {u.email} and Password: {u.password}, thank you'
            message = sms_client.messages.create(
                body=sms_message,
                from_=os.getenv("YOUR_TWILIO_PHONE_NUMBER"),
                to=u.mobilephone
            )

            # Update sms_delivered based on Twilio response
            if message.status == "delivered":
                print(f"{'STATUS:SUCCESS'}:{message}")  # log success messages
                u.smsdelivered = True
            else:
                print(f"{'STATUS:FAILED'}:{message}")  # log failed messages
                u.smsdelivered = False
            u.save()

        time.sleep(1800)  # Sleep for 30 minutes
