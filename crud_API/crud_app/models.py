from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Employee(models.Model):
  first_name   = models.CharField(max_length=200)
  last_name    = models.CharField(max_length=200)
  phone_number = models.CharField(max_length=11)
  email        = models.EmailField(max_length = 100) 
  join_date    = models.DateTimeField()
  created_date = models.DateTimeField(default=timezone.now)

  def __str__(self):
    return self.first_name