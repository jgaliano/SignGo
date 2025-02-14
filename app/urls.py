from django.urls import path, include
from . import views
from .views import CustomLoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('helloworld/', views.helloworld, name='helloworld'),
    path('home/', views.home, name="home"),
    path('', views.home, name="home"),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('salir/', views.salir, name='salir'),
    path('users/', views.administrar_usuarios, name='users'),
    path('users/crear/', views.crear_usuario, name='crear_usuario'),
    path('users/editar/<str:token_user>/', views.editar_usuario, name='editar_usuario'),
    path('empresas/', views.administrar_empresas, name='empresas'),
    path('empresas/crear/', views.crear_empresa, name='crear_empresa'),
    path('empresas/editar/<str:token_emp>/', views.editar_empresa, name='editar_empresa'),
    path('licencias/', views.licencias, name="licencias"),
    path('licencias/crear/', views.licencias_crear, name="licencias_crear"),
    path('licencias/editar/<str:token_lc>/', views.licencias_editar, name="licencias_editar"),
    path('licencias/renovar/<str:token_rlc>/', views.licencias_renovar, name="renovar_licencia"),
    path('licencias/compra_extra/<str:token_lc>/', views.compra_extra, name="compra_extra"),
    path('billing/', views.adminBilling, name="billing"),
    path('hostIP/', views.hostIP, name="hostIP"),
    path('hostIP/tokens/', views.validate_tokens_api_oneshot, name="tokens"),
    path('hostIP/crear_token/', views.crear_token, name="crear_token"),
    path('acceso-denegado/', views.accesoDenegado, name="accesoDenegado"),
    path('accounts/password_reset/', views.password_reset, name='password_reset'),
    path('accounts/reset/<uidb64>/<token>/', views.password_reset_change ,name='password_reset_confirm'),
    # path('users/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    # path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    # path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]