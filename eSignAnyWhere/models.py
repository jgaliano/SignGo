from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class documentos(models.Model):
    nombreArchivos = ArrayField(models.CharField(max_length=200, null=True))
    nombreCarpeta = models.CharField(max_length=250)
    request = models.CharField(max_length=50, null=True)
    estatus = models.CharField(max_length=50, null=True)
    
class firmante(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.CharField(max_length=100)
    sobre = models.CharField(max_length=100, null= True)
    tipo = models.CharField(max_length=100, null=True)
    request = models.CharField(max_length=100, null=True)
    envelope = models.CharField(max_length=100, null=True)
    idFiles = models.CharField(max_length=100, null=True)


