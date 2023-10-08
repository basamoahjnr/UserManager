from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Registration(models.Model):
    first_name = models.CharField(max_length=50,
                                  null=False)
    last_name = models.CharField(max_length=50,
                                 null=False)
    email = models.EmailField(null=False,
                              db_index=True,
                              unique=True)
    password = models.CharField(max_length=8, null=True)
    telephone_number = PhoneNumberField(null=False, blank=False, unique=True, region='GH')
    profile = models.CharField(max_length=60, null=True)
    terms_and_conditions = models.BooleanField(default=False)
    is_enabled = models.BooleanField(default=False)
    sms_delivered = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_created=True,
                                      auto_now=True)

    class Meta:
        db_table = "registration"


class RadCheck(models.Model):
    username = models.CharField(max_length=255)
    attribute = models.CharField(max_length=64)
    value = models.CharField(max_length=255)
    op = models.CharField(max_length=2)

    class Meta:
        db_table = 'radcheck'
        managed = False  # Use the 'radius' database connection


class RadGroupCheck(models.Model):
    groupname = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'radgroupcheck'
        managed = False  # Use the 'radius' database connection


class RadUserGroup(models.Model):
    username = models.CharField(max_length=255)
    groupname = models.CharField(max_length=64)
    priority = models.IntegerField()

    class Meta:
        db_table = 'radusergroup'
        managed = False  # Use the 'radius' database connection


class RadGroupReply(models.Model):
    groupname = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=255)

    # Define a ForeignKey or OneToOneField to represent the association
    radcheck = models.ForeignKey(RadCheck, on_delete=models.CASCADE, related_name='group_replies', null=True,
                                 blank=True)
    radgroupcheck = models.ForeignKey(RadGroupCheck, on_delete=models.CASCADE, related_name='group_replies', null=True,
                                      blank=True)
    radusergroup = models.ForeignKey(RadUserGroup, on_delete=models.CASCADE, related_name='group_replies', null=True,
                                     blank=True)

    class Meta:
        db_table = 'radgroupreply'
        managed = False
