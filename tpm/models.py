from django.db import models

from django.contrib.auth.models import AbstractUser

class Sessions(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    sessionKey = models.TextField(default='none')
    
    def __str__(self):
        return self.sessionKey

class User(AbstractUser):
    sessionId = models.OneToOneField('Sessions', on_delete=models.CASCADE,  verbose_name=u"Сессия", null=True)

# Create your models here.