from django.core.management.base import BaseCommand
from faker import Faker
from faker_e164.providers import E164Provider

from UserManager.models import UserInfo  # Import your Registration model

fake = Faker()
fake.add_provider(E164Provider)

# To fake an e164 phone number
fake.e164(region_code="GH", valid=True, possible=True)


class Command(BaseCommand):
    help = 'Generate and insert 100 fake users into the Registration table'

    def handle(self, *args, **kwargs):
        for _ in range(100):
            UserInfo.objects.create(
                firstname=fake.first_name(),
                lastname=fake.last_name(),
                email=fake.email(),
                termsandconditions=True,
                mobilephone=fake.e164(region_code="GH", valid=True, possible=True),
            )
