from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    description = models.CharField(max_length=80)
    date = models.DateField()
    time = models.TimeField()
    time_to = models.TimeField(null=True)
    repeat = models.BooleanField(default=False)

class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    is_approve = models.BooleanField(default=False)
