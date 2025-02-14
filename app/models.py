from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from django.utils.timezone import now

# Modelos para creación, administración y mantenimiento de usuarios, empresas y licencias
class UsuarioSistema(models.Model):
    id = models.AutoField(primary_key=True)
    Nombres = models.CharField(max_length=50, null=True)
    Apellidos = models.CharField(max_length=50, null=True)
    Email = models.CharField(max_length=50, null=True)
    Celular = models.CharField(max_length=50, null=True)
    CUI = models.CharField(max_length=50, null=True)
    FechaRegistro = models.DateField(auto_now_add=True, null=True)
    Token = models.CharField(max_length=100, null=True)
    UsuarioGeneral = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return self.id

class EmpresaSistema(models.Model):
    id = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=50)
    NIT = models.CharField(max_length=50, null=True)
    Sector = models.CharField(max_length=50, null=True)
    NombreContacto = models.CharField(max_length=50, null=True)
    NumeroContacto = models.CharField(max_length=50, null=True)
    EmailContacto = models.CharField(max_length=50, null=True)
    FechaRegistro = models.DateField(auto_now_add=True, null=True)
    Estado = models.BooleanField(default=True)
    Token = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return self.id
    
class PerfilSistema(models.Model):
    id = models.AutoField(primary_key=True)
    empresa = models.ForeignKey(EmpresaSistema, null=True, blank=True, on_delete=models.CASCADE, related_name='usuarios')
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    Token = models.CharField(max_length=100, null=True)
    
class LicenciasSistema(models.Model):
    id = models.AutoField(primary_key=True)
    empresa = models.ForeignKey(
        EmpresaSistema, 
        on_delete=models.CASCADE, 
        related_name="licencias", 
        null=True, 
        blank=True
    )
    usuario = models.ForeignKey(
        UsuarioSistema, 
        on_delete=models.SET_NULL, 
        related_name="licencias", 
        null=True, 
        blank=True
    )
    tipo = models.CharField(max_length=50, null=True)
    modalidad = models.CharField(max_length=50, null=True)
    costo_tipo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cantidad_creditos = models.IntegerField()
    acumulado_creditos = models.IntegerField(null=True)
    costo_creditos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_fin = models.DateField()
    activa = models.CharField(max_length=50, null=True)
    usuario_billing = models.CharField(max_length=50, null=True)
    contrasena_billing = models.CharField(max_length=50, null=True)
    observaciones = models.TextField(null=True)
    consumo = models.IntegerField(null=True, default=0)
    TokenAuth = models.CharField(max_length=100, null=True)
    porcentaje = models.FloatField(default=0, editable=False)
    env = models.CharField(max_length=20, null=True)
    
    def save(self, *args, **kwargs):
        if self.acumulado_creditos > 0:
            self.porcentaje = (self.consumo / self.acumulado_creditos) * 100
        else:
            self.porcentaje = 0 
        super().save(*args, **kwargs)
        
    def licencia_vencida(self):
        return self.fecha_fin < now().date()
    
    def clean(self):
        """Valida que la licencia esté asociada a una empresa o a un usuario."""
        if not self.empresa and not self.usuario:
            raise ValidationError("La licencia debe estar asociada a una empresa o a un usuario.")

    def __str__(self):
        return f"Licencia {self.id} ({self.tipo})"
    
    
class RenovacionLicencia(models.Model):
    id = models.AutoField(primary_key=True)
    licencia = models.ForeignKey(LicenciasSistema, on_delete=models.CASCADE, related_name="renovaciones")
    fecha_renovacion = models.DateField(auto_now_add=True)
    fecha_anterior_emision = models.DateField(null=True)
    fecha_anterior_fin = models.DateField(null=True)
    fecha_inicio = models.DateField(null=True)
    fecha_fin = models.DateField(null=True)
    costo_tipo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costo_creditos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cantidad_creditos = models.IntegerField()
    Token = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"Renovación {self.id} para Licencia {self.licencia.id}"
    
class CompraExtraordinaria(models.Model):
    cantidad_creditos = models.IntegerField()
    precio_creditos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    licencia = models.ForeignKey(LicenciasSistema, on_delete=models.CASCADE, related_name="compra_extra", null=True)
    fecha_compra = models.DateField(auto_now_add=True)
    
    
class token_oneshot(models.Model):
    token = models.CharField(max_length=100, null=True)
    