from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class Sessions(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    sessionKey = models.TextField(default='none')
    
    def __str__(self):
        return self.sessionKey


class User(AbstractUser):
    sessionId = models.OneToOneField('Sessions', on_delete=models.CASCADE,  verbose_name=u"Сессия", null=True)


class Task(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['complete']
