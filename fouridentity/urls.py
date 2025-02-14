from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('helloworld/', views.helloworld, name='helloworld'),
    path('home_4identity/', views.home_4identity, name="home_4identity"),
    path('sign_4identity/', views.upload_file, name="sign_4identity"),
    path('sign-end-ok/', views.sign_end_ok, name='sign_end_ok'),
    path('sign-end-error/', views.sign_end_error, name='sign_end_error'),
    path('done_4identity/', views.done_4identity, name="done_4identity"),
]

