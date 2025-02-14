from django.db import models
import os
import environ
from pathlib import Path
from django.contrib.postgres.fields import ArrayField
from datetime import timedelta

class Envio(models.Model):
    nombre_envio = models.CharField(max_length=255)
    flujo_por_orden = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    TokenAuth = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.nombre_envio

class Firmante(models.Model):
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE, related_name="firmantes")
    correo = models.EmailField()
    nombres = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    tipo_firma = models.CharField(max_length=50)
    TokenAuth = models.CharField(max_length=100, null=True)
    Datos = models.BooleanField(default=False)
    is_firmado = models.BooleanField(default=False)
    is_enviado = models.BooleanField(default=False, null=True)
    orden_flujo = models.CharField(max_length=50, null=True)
    fecha_enviado = models.DateTimeField(null=True, blank=True, default=None)
    fecha_firmado = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return self.id
    
# Create your models here.
class documentos(models.Model):
    status = models.CharField(max_length=15)
    secret = models.TextField()
    nameArchivos = ArrayField(models.TextField(null=True), null=True)
    idRequest = models.CharField(max_length=8, null=True)
    nameCarpeta = models.CharField(max_length=25, null=True)
    cantidadDocumentos = models.CharField(max_length=25, null=True)
    url_archivos = ArrayField(models.TextField(null=True), null=True)
    tokenEnvio = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return self.idmodels.CharField(max_length=25, null=True)
    

def dynamic_upload_to(instance, filename, base_path="media/", folder_name="default"):
    """Genera una ruta de subida dinámica."""
    return f"{base_path}/{folder_name}/{filename}"


BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env.dev'))

class Imagen(models.Model):
    UsuarioFirmante = models.ForeignKey(Firmante, on_delete=models.CASCADE, related_name="firmante_imagen", null=True)
    presigned_url = models.TextField(null=True)
    imagen = models.FileField(upload_to="dynamic_path", null=True)
    
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

    def get_presigned_url(self, expiration=604800):
        """Genera una URL firmada para el archivo."""
        import boto3
        from django.conf import settings

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
        return url


class DatosFirmante(models.Model):
    Firmante = models.ForeignKey(Firmante, on_delete=models.CASCADE, related_name="firmante_datos", null=True)
    dpi = models.CharField(max_length=50)
    celular = models.CharField(max_length=50)
    direccion = models.TextField()
    with_video = models.BooleanField(default=False)
    imagen_dpi_frontal = models.ForeignKey(Imagen, on_delete=models.CASCADE, related_name="imagen_frontal", null=True)
    imagen_dpi_posterior = models.ForeignKey(Imagen, on_delete=models.CASCADE, related_name="imagen_posterior", null=True)
    imagen_persona = models.ForeignKey(Imagen, on_delete=models.CASCADE, related_name="imagen_persona", null=True)


 
    
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
    def get_presigned_url(self, expiration=604800): # 604800
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
    
class uploadDocument(models.Model):
    nombre_documento = models.TextField()
    url_documento = models.TextField()
    envio = models.CharField(max_length=100)
    is_firmanto = models.BooleanField(default=False)
    
    def __str__(self):
        return self.id
    
class detalleFirma(models.Model):
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE, related_name="envio_detalle")
    firmante = models.ForeignKey(Firmante, on_delete=models.CASCADE, related_name="firmante_detalle", null=True)
    documento = models.ForeignKey(uploadDocument, on_delete=models.CASCADE, related_name="document_detalle", null=True)
    pagina = models.CharField(max_length=50)
    p_x1 = models.CharField(max_length=50)
    p_x2 = models.CharField(max_length=50)
    p_y1 = models.CharField(max_length=50)
    p_y2 = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default="NoFirmado")
    request_upload_document = models.TextField(null=True)
    
    def __str__(self):
        return self.id
    
class log_oneshot(models.Model):
    log = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    Firmante = models.ForeignKey(Firmante, on_delete=models.CASCADE, related_name="firmante_log", null=True)
    status = models.TextField(null=True)
    detail = models.TextField(null=True)
    
class VitacoraFirmado(models.Model):
    TokenEnvio = models.TextField()
    NombreArchivo = models.TextField()
    TokenArchivo = models.TextField()
    UsuarioFirmante = models.ForeignKey(Firmante, on_delete=models.CASCADE, null=True)
    EstadoFirma = models.TextField(null=True)
    IDArchivoAPI = models.TextField(null=True)
    FechaFirmado = models.DateField(auto_now_add=True, null=True)
    url_archivo = models.TextField(null=True)
    documento_id = models.ForeignKey(uploadDocument, on_delete=models.CASCADE, related_name="documento_id", null=True)
    
class VideoIdentificacion(models.Model):
    status = models.TextField()
    date = models.DateTimeField()
    previous_status = models.TextField()
    request = models.CharField(max_length=15)
    registration_authority = models.CharField(max_length=10)
    firmante = models.ForeignKey(Firmante, on_delete=models.CASCADE, related_name="firmante_video")
    
    
    
