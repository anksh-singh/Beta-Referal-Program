from django.db import models

# Create your models here.
class User(models.Model):
    email = models.EmailField()
    referral_id = models.UUIDField()