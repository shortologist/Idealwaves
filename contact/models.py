from django.db import models
from django.contrib.auth.models import User


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")
    mobile = models.CharField(max_length=20, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)