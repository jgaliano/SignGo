from django.db import models
from django.contrib.postgres.fields import ArrayField

class volIP(models.Model):
    ip = models.CharField(max_length=50, default='192.168.11.16:8080')
    protocol = models.CharField(max_length=10, null=True, default="0")
    
class documentos(models.Model):
    nombreArchivos = ArrayField(models.CharField(max_length=200, null=True))
    nombreCarpeta = models.CharField(max_length=250)
    request = models.CharField(max_length=10, null=True)
    
class requestValidation(models.Model):
    requestVol = models.CharField(max_length=15)
    identificador = models.CharField(max_length=50, null=True)
    result = ArrayField(models.CharField(max_length=250, null=True))
    documento = models.CharField(max_length=150, null=True)
    