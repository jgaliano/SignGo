from django.urls import path
from . import views

urlpatterns = [
    path('helloworld/', views.helloworld, name='helloworld'),
    path('plantilla/', views.plantilla, name='plantilla'),
    path('contactos/', views.contactos, name='contactos'),
    path('subir-csv/', views.subir_csv, name='subir_csv'),
    path('envios/', views.envios, name='envios'),
    path('envio/<str:token>/', views.envio, name='envio'),
    path('verifyDocs/<str:token>/<str:request_id>/<str:secretToken>', views.verifyDocs, name="verifyDocs"),
    path('signDocs/<str:tokenSign>/<str:request_id>/<str:secretToken>', views.verifySignDocs, name="signDocs"),
    path('admin/', views.admin, name='admin'),   
    path('crearEmpresa/', views.crearEmpresa, name='crearEmpresa'),   
    path('empresas/', views.empresas, name='empresas'),
    path('crearUsuario/', views.signbolCrearuser, name='crearUsuario'),
    path('usersSignbol/', views.usersSignbol, name='usersSignbol'),
    path('usersCreate/', views.usersCreate, name='usersCreate'),
    path('reportes/', views.reportes, name="reportes"),
    path('buscar_empresas/', views.buscar_empresas, name='buscar_empresas'),
    path('EditUsuarioSignbol/<str:token>/', views.EditUsuarioSignbol, name='EditUsuarioSignbol'),
    path('DetalleContacto/<str:token>/', views.detalleContacto, name='DetalleContacto'),
    path('generar-reporte/', views.generar_reporte_pdf, name='generar-reporte'),
    path('reporteDetalleEnvio/<str:token>/', views.reporteDetalleEnvio, name='reporteDetalleEnvio'),
    path('reenviarCorreo/<str:token>/', views.reenviarCorreo, name='reenviarCorreo'),
    path('UI_prueba_plantilla/', views.UI_prueba_plantilla, name='UI_prueba_plantilla'),
    path('descargarArchivos/<str:token>/', views.descargarArchivos, name='descargarArchivos'),
]