from django.db import models

# Create your models here.


class Account(models.Model):
    email = models.CharField(
        primary_key=True, max_length=30, null=False, default='-')
    name = models.CharField(max_length=10)
    user_id = models.CharField(max_length=20, null=False)
    user_pw = models.CharField(max_length=20, null=False)
