from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class UserInfo(models.Model):
    firstname = models.CharField(max_length=200, blank=True)
    lastname = models.CharField(max_length=200, blank=True)
    username = models.CharField(max_length=128, blank=True)
    email = models.EmailField(max_length=200, blank=True,
                              unique=True)
    portalloginpassword = models.CharField(max_length=128, blank=True)
    mobilephone = PhoneNumberField(unique=True, region='GH', max_length=200, blank=True)
    # REMEMBER TO CREATE THIS FIELDS IN THE USERINFO TABLE
    termsandconditions = models.BooleanField(default=False)
    isenabled = models.BooleanField(default=False)
    smsdelivered = models.BooleanField(default=False)
    twilio_sid = models.CharField(max_length=200, blank=True, null=True)
    profile = models.CharField(max_length=60, blank=True)
    creationdate = models.DateTimeField(auto_now_add=True)
    updatedate = models.DateTimeField(auto_created=True,
                                      auto_now=True)

    class Meta:
        db_table = "userinfo"


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

    class Meta:
        db_table = 'radgroupreply'
        managed = False
