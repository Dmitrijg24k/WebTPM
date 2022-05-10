from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass

# Create your models here.
class Sessions(models.Model):
    numberSession = models.IntegerField(unique=True)
    sessionKey = models.TextField(default='none')
    
    def __str__(self):
        return self.sessionKey