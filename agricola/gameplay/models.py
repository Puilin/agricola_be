from django.db import models

# Create your models here.
class Account(models.Model):
    email = models.CharField(max_length=30, null=True)
    name = models.CharField(max_length=10)
    user_id = models.CharField(max_length=20, null=True)
    user_pw = models.CharField(max_length=20, null=True)