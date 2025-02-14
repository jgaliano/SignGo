from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import environ
import os
from pathlib import Path
from datetime import timedelta

User = get_user_model()

def user_directory_path(instance, filename):
    # Almacena el archivo en media/usuario_<id>/<nombre_de_archivo>
    return f'signbox/Rubrica/user_{instance.UsuarioSistema.id}/{filename}'

# Create your models here.
class documentos(models.Model):
    status = models.CharField(max_length=15)
    secret = models.TextField()
    nameArchivos = ArrayField(models.TextField(null=True), null=True)
    idRequest = models.CharField(max_length=8, null=True)
    nameCarpeta = models.CharField(max_length=25, null=True)
    cantidadDocumentos = models.CharField(max_length=25, null=True)
    url_archivos = ArrayField(models.TextField(null=True), null=True)
    
    def __str__(self):
        return self.idmodels.CharField(max_length=25, null=True)
    
class VitacoraFirmado(models.Model):
    TokenEnvio = models.TextField()
    NombreArchivo = models.TextField()
    TokenArchivo = models.TextField()
    UsuarioFirmante = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    EstadoFirma = models.TextField(null=True)
    IDArchivoAPI = models.CharField(max_length=50, null=True)
    FechaFirmado = models.DateField(auto_now_add=True, null=True)
    url_archivo = models.TextField(null=True)
    

class billingSignboxProd(models.Model):
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    status = models.CharField(max_length=25, null=True)
    
class billingSignboxSandbox(models.Model):
    user = models.CharField(max_length=50)
    password = models.CharField(max_length=100)
    status = models.CharField(max_length=25, null=True)


class signboxAPI(models.Model):
    ip = models.CharField(max_length=50, default='192.168.11.16:8080')
    protocol = models.CharField(max_length=10, null=True, default="0")
    
class estiloFirmaElectronica(models.Model):
    UsuarioSistema = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    Rubrica = models.TextField()
    imagen_archivo = models.ImageField(upload_to=user_directory_path, null=True)
    dimensionesImagen = models.CharField(max_length=50, null=True)
    isNombre = models.BooleanField(default=False, null=True)
    isFecha = models.BooleanField(default=False, null=True)
    isUbicacion = models.BooleanField(default=False, null=True)
    is_predeterminado = models.BooleanField(default=False, null=True)
    
    
def dynamic_upload_to(instance, filename, base_path="media/", folder_name="default"):
    """Genera una ruta de subida dinámica."""
    return f"{base_path}/{folder_name}/{filename}"


BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env.dev'))


class Imagen(models.Model):
    UsuarioSistema = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    url_firmada_expiracion = models.DateTimeField(null=True, blank=True)
    Rubrica = models.TextField()
    imagen = models.FileField(upload_to="dynamic_path", null=True)
    dimensionesImagen = models.TextField(null=True)
    isNombre = models.BooleanField(default=False, null=True)
    isFecha = models.BooleanField(default=False, null=True)
    isUbicacion = models.BooleanField(default=False, null=True)
    is_predeterminado = models.BooleanField(default=False, null=True)
    presigned_url = models.TextField(null=True)
    
    def __str__(self):
        return self.imagen.name

    def save(self, *args, **kwargs):
        # Define las rutas dinámicas
        base_path = getattr(self, "_base_path", "media/")
        folder_name = getattr(self, "_folder_name", "default")
        self.imagen.field.upload_to = lambda instance, filename: dynamic_upload_to(instance, filename, base_path, folder_name)
        super().save(*args, **kwargs)

    def set_upload_paths(self, base_path, folder_name):
        """Define el path base y la carpeta."""
        self._base_path = base_path
        self._folder_name = folder_name
    # 604800
    def get_presigned_url(self, expiration=604800):
        """Genera una URL firmada para el archivo."""
        import boto3
        from django.conf import settings
        from datetime import datetime, timezone

        s3_client = boto3.client(
            's3',
            aws_access_key_id=env('AWS_ACCESS_KEY'),
            aws_secret_access_key=env('AWS_SECRET_KEY'),
            region_name=env('AWS_REGION_NAME'),
        )
        bucket_name = env('AWS_BUCKET_NAME')
        object_name = self.imagen.name

        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=expiration
        )
        self.url_firmada_expiracion = datetime.now(timezone.utc) + timedelta(seconds=expiration)
        self.save(update_fields=["url_firmada_expiracion"])
        return url


class ArchivosPDF(models.Model):
    archivo = models.FileField(upload_to="dynamic_path", null=True, max_length=255)
    url_firmada_expiracion = models.DateTimeField(null=True, blank=True)
    token_archivo = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.archivo.name

    def save(self, *args, **kwargs):
        # Define las rutas dinámicas
        base_path = getattr(self, "_base_path", "media/")
        folder_name = getattr(self, "_folder_name", "default")
        self.archivo.field.upload_to = lambda instance, filename: dynamic_upload_to(instance, filename, base_path, folder_name)
        super().save(*args, **kwargs)

    def set_upload_paths(self, base_path, folder_name):
        """Define el path base y la carpeta."""
        self._base_path = base_path
        self._folder_name = folder_name
    # 604800
    def get_presigned_url(self, expiration=604800):
        """Genera una URL firmada para el archivo."""
        import boto3
        from django.conf import settings
        from datetime import datetime, timezone

        s3_client = boto3.client(
            's3',
            aws_access_key_id=env('AWS_ACCESS_KEY'),
            aws_secret_access_key=env('AWS_SECRET_KEY'),
            region_name=env('AWS_REGION_NAME'),
        )
        bucket_name = env('AWS_BUCKET_NAME')
        object_name = self.archivo.name

        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=expiration
        )
        
        self.url_firmada_expiracion = datetime.now(timezone.utc) + timedelta(seconds=expiration)
        self.save(update_fields=["url_firmada_expiracion"])
        return url
    
class credencialesCert(models.Model):
    user_system = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    usuario_cert = models.CharField(max_length=25, null=True)
    pass_cert = models.CharField(max_length=25, null=True)
    
class documentos_eliminados(models.Model):
    nombre_documento = models.CharField(max_length=100, null=True)
    usuario_firmante = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    fecha_eliminacion = models.DateField(auto_now_add=True, null=True)
    
class detalleFirma(models.Model):
    TokenAuth = models.CharField(max_length=100, null=True)
    documento = models.TextField()
    nombre_documento = models.CharField(max_length=100, null=True)
    pagina = models.CharField(max_length=50)
    p_x1 = models.CharField(max_length=50)
    p_x2 = models.CharField(max_length=50)
    p_y1 = models.CharField(max_length=50)
    p_y2 = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default="NoFirmado")
    request_upload_document = models.TextField(null=True)
    
    def __str__(self):
        return self.id
    
class detalleDocumento(models.Model):
    TokenAuth = models.CharField(max_length=100, null=True)
    url_documento = models.TextField()
    nombre_documento = models.TextField()


    
    
    

    
    