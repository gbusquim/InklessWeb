from django.db import models

# Create your models here.
class Nome(models.Model):
    primeiroNome = models.CharField(max_length=300)
    objects = models.Manager()