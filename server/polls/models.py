import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)
    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text
    
class User(models.Model):
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    direction = models.CharField(max_length=200)
    last_login = models.DateTimeField("last login",auto_now_add=True)
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.username