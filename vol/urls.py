from django.urls import path
from . import views

urlpatterns = [
    path('helloworld/', views.helloworld, name='helloworld'),
    path('home/', views.home, name='home'),
    path('verifyDocs/<int:requestID>', views.verificarDocumentos, name="verifyDocs"),
    path('validate/<int:requestID>', views.documentosValidados, name="validate")
]