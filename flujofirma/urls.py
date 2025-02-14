from django.urls import path
from . import views

urlpatterns = [
    path('helloworld/', views.helloworld, name='helloworld'),
    path('crear_flujo/', views.crear_flujo, name='crear_flujo'),
    path('progreso_flujo/<str:tokenEnvio>/', views.progreso_flujo, name='progreso_flujo'),
    path('datos_firmante/<str:tokenFirmante>/', views.datos_firmantes, name="datos_firmantes"),
    path('confirmacion_envio/<str:tokenEnvio>/', views.confirmacion_envio_flujo, name="confirmacion_envio"),
    path('upload_files/<str:tokenEnvio>/', views.upload_files, name="upload_files"),
    path('asignar_firma/<str:tokenEnvio>/', views.asignar_firma, name="asignar_firma"),
    path('validar_documento/<str:tokenFirmante>/', views.validar_documento, name="validar_documento"),
    path('aprobar_video/', views.aprobar_video, name="aprobar_video"),
    path('aprobacion_video_id_oneshot_temporal/', views.aprobacion_video_id_oneshot_temporal, name="aprobacion_video_id_oneshot_temporal"),
    path('firmar_documento_cld/<str:tokenFirmante>/', views.firmar_documento_cld, name="firmar_documento_cld"),
    path('firmar_documento_oneshot/<str:tokenFirmante>/', views.firmar_documento_oneshot, name="firmar_documento_oneshot"),
    path('firmado/<str:tokenFirmante>/', views.firmado, name="firmado"),
    path('videoid/', views.videoid, name="videoid"),
    path('get_token/', views.get_token, name="get_token"),
    path('confirmacion_firmado/<str:tokenFirmante>/', views.confirmacion_firmado, name="confirmacion_firmado"),
    path('historial_flujos/', views.historial_flujos, name="historial_flujos"),
]