from django.core.management.base import BaseCommand
from faker import Faker
from faker_e164.providers import E164Provider

from UserManager.models import Registration  # Import your Registration model

fake = Faker()
fake.add_provider(E164Provider)

# To fake an e164 phone number
fake.e164(region_code="GH", valid=True, possible=True)


class Command(BaseCommand):
    help = 'Generate and insert 100 fake users into the Registration table'

    def handle(self, *args, **kwargs):
        for _ in range(100):
            Registration.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                terms_and_conditions=True,
                telephone_number=fake.e164(region_code="GH", valid=True, possible=True),
            )
