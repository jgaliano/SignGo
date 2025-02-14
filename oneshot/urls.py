from django.urls import path
from . import views

urlpatterns = [
    path('helloworld/', views.helloworld, name='helloworld'), 
    path('solicitud/', views.formulario, name="solicitud"),
    path('one_shot_docs/', views.one_shot_cargarPDFs, name="one_shot_docs"),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('sendOtp/', views.sendOtpOneShot, name="sendOtp"),
    path('one_shot_sign', views.one_shot_sign, name="one_shot_sign"),
    path('one_shot_Firmados', views.one_shot_Firmados, name='one_shot_Firmados'),
    path('historial/', views.oneShot_solicitudes, name='oneShot_solicitudes'),
    path('busquedaOperados/<int:requestID>', views.busquedaOperados, name="busquedaOperados"),
    path('oneshot_done/', views.oneshot_done, name='oneshot_done'),
    path('aprobarOneshot/<int:requestID>', views.aprobarOneshot, name='aprobarOneshot'),
    path('aprobarVideo/<int:requestID>', views.validarInfo, name='validarInfo'),
]