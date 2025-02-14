from django.urls import path
from . import views

urlpatterns = [
    path('result/<str:carpeta>/<str:name>', views.url_out, name='url_out'),
    path('services/<str:name>', views.urlback, name='urlback'),
    path('resultPlanilla/<str:carpeta>/<str:id>/<str:name>', views.url_out_planilla, name='url_out_planilla'),
]

    