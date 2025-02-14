from django.urls import path
from . import views

urlpatterns = [
    path('helloworld/', views.helloworld, name="helloworld"),
    path('uploadFile/', views.uplaodFile, name="uploadFile"),
    path('viewDocument/<int:requestID>', views.viewDocument, name="viewDocument"),
    path('formData/<int:requestID>', views.formData, name="formData"),
    path('confirmacionEnvio/<int:requestID>', views.confirmacionEnvio, name="confirmacionEnvio"),
    path('solicitudes/', views.solicitudes, name="solicitudes"),
    path('solicitud/<int:requestID>', views.solicitud, name="solicitud"),
]