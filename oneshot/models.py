from django.db import models
from django.contrib.postgres.fields import ArrayField

class cliente(models.Model):
    id = models.AutoField(primary_key=True)
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50)
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    direccion = models.CharField(max_length=100)
    dpi = models.CharField(max_length=15)
    celular = models.CharField(max_length=8)
    fecha = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=50, null=True)
    tipo = models.CharField(max_length=50, null=True)
    
    def __str__(self):
        return self.id
    
class requestSign(models.Model):
    id = models.AutoField(primary_key=True)
    id_request = models.CharField(max_length=8)
    id_video = models.CharField(max_length=6, null=True)
    id_cliente = models.ForeignKey(cliente, on_delete=models.CASCADE, related_name='cliente')
    fecha = models.DateTimeField(auto_now_add=True)
    transaction_cliente = models.CharField(max_length=100)
    transaction_operador = models.CharField(max_length=100)
    correo_operador = models.CharField(max_length=50, null=True)
    username_operador = models.CharField(max_length=50, null=True)
    aprovado = models.CharField(max_length=50, null=True)
    
    def __str__(self):
        return str(self.id)
    
class documentos(models.Model):
    id = models.AutoField(primary_key=True)
    id_request = models.CharField(max_length=8, null=True)
    status = models.TextField(null=True)
    transaction = models.TextField(null=True)
    name_archivos = ArrayField(models.CharField(max_length=250, null=True))
    
class billingOneshotProd(models.Model):
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    status = models.CharField(max_length=25, null=True)
    
class billingOneshotSandbox(models.Model):
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    status = models.CharField(max_length=25, null=True)
    
class oneshotAPI(models.Model):
    ip = models.CharField(max_length=50, default='192.168.11.16:8080')
    protocol = models.CharField(max_length=10, null=True, default="0")
    
