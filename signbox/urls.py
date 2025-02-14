from django.urls import path
from . import views

urlpatterns = [
    path('helloworld/', views.helloworld, name='helloworld'),
    path('uploadFiles/', views.uploadFiles, name="uploadFiles"),
    # path('verifyDocs/<str:request_id>', views.verifyDocs, name="verifyDocs"),
    path('verifyDocs/<str:tokenEnvio>', views.asignar_firma, name="verifyDocs"),
    path('firma_lote/<str:tokenEnvio>', views.firma_lote, name="firma_lote"),
    path('signDocs/<str:request_id>', views.verifySignDocs, name="signDocs"),
    path('historial/', views.historial, name='historial'),
    path('historial/enviar_correo/', views.enviar_correo, name='enviar_correo'),
    path('historial/eliminar_documento/<int:TokenAuth>/', views.eliminar_documento, name="eliminar_documento"),
    path('historial/validar_url/', views.validar_url, name="validar_url"),
    path('generar-reporte/', views.generar_reporte, name='generar-reporte'),
    path('personalizar/', views.personalizar, name="personalizar"),
    path('personalizar/eliminar_estilo/<int:TokenAuth>/', views.eliminar_estilo, name="eliminar_estilo"),
    path('guardar_imagen/', views.guardar_imagen, name="guardar_imagen"),
    path('select_imagen/<int:estilo_id>/', views.select_imagen, name="select_imagen"),
    path('watchDocument/<str:id_request>/', views.watchDocument, name='watchDocument'),
    # path('verifyTemporal/<str:tokenEnvio>/', views.asignar_firma, name="asignar_firma_signbox")
]