from django.db import models
from django.contrib.auth.models import User



class Empresa(models.Model):
    id = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=50)
    NIT = models.CharField(max_length=50, null=True)
    Ciudad = models.CharField(max_length=150, null=True)
    Sector = models.CharField(max_length=50, null=True)
    FechaRegistro = models.DateField(auto_now_add=True, null=True)
    Estado = models.CharField(max_length=50,  null=True)
    TokenAuth = models.CharField(max_length=50, null=True)
    
    def __str__(self):
        return self.id
    
class ListaContactos(models.Model):
    nombre = models.CharField(max_length=50, null=True)
    tokenAuth = models.CharField(max_length=50, null=True)
    Empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='listacontactoEmpresa', null=True)
    CantidadContactos = models.CharField(max_length=50, null=True)
    FechaCreacion = models.DateField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.nombre or "ListaContactos sin nombre"

class Contacto(models.Model):
    Nombres = models.CharField(max_length=50, null=True)
    Apellidos = models.CharField(max_length=50, null=True)
    Email = models.CharField(max_length=50, null=True)
    Celular = models.CharField(max_length=50, null=True)
    Salario = models.CharField(max_length=50, null=True)
    Departamento = models.CharField(max_length=50, null=True)
    Puesto = models.CharField(max_length=50, null=True)
    Periodo = models.CharField(max_length=50, null=True) 
    tokenAuth = models.CharField(max_length=50, null=True)
    lista_contactos = models.ForeignKey(ListaContactos, on_delete=models.CASCADE, related_name='contactos', null=True)
    Empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='contactoEmpresa', null=True)
    
    def __str__(self):
        return f"{self.Nombres} {self.Apellidos}"

class Plantilla(models.Model):
    Nombre = models.CharField(max_length=50)
    Contenido = models.TextField()
    Empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='empresaPlantilla', null=True)
    
    def __str__(self):
        return self.Nombre

class PerfilUsuario(models.Model):
    empresa = models.ForeignKey(Empresa, null=True, blank=True, on_delete=models.CASCADE, related_name='usuarios')
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tokenAuth = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return f"{self.usuario.username} - {self.empresa.Nombre}"
    
    
class Envios(models.Model):
    Plantilla = models.ForeignKey(Plantilla, on_delete=models.CASCADE, related_name='envios')
    ListaContactos = models.ForeignKey(ListaContactos, on_delete=models.CASCADE, related_name='envios')
    TokenAuth = models.CharField(max_length=50, null=True)
    Empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='envios', null=True)
    NombreEnvio = models.CharField(max_length=50, null=True)
    UsuarioRemitente = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='usuarioEnvio', null=True)
    fechaEnvio = models.DateField(auto_now_add=True, null=True)
    TotalEnvios = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return f"Envio {self.id} - {self.Empresa.Nombre}"
    
class VitacoraEnvios(models.Model):
    nombre = models.CharField(max_length=50, null=True)
    remitente = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='usuarioRemitente')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='empresaRemitente')
    fechaEnvio = models.DateField(auto_now_add=True)
    fechaFirma = models.DateField(null=True)
    token = models.CharField(max_length=100, null=True)
    scratchcard = models.CharField(max_length=25, null=True)
    envioVitacora = models.ForeignKey(Envios, on_delete=models.CASCADE, related_name='envioVitacora', null=True)
    status = models.CharField(max_length=25, null=True)
    tokenAuthLista = models.CharField(max_length=100, null=True)
    idUsuario = models.ForeignKey(Contacto, on_delete=models.CASCADE, related_name='envioUsuario', null=True)
    
    def __str__(self):
        return self.id
    
    

    

