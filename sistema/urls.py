from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include


urlpatterns = [
    path('signgoAdmin/', admin.site.urls),
    path('', include('app.urls')),
    path('firma_agil/', include('signbox.urls')),
    path('4identity/', include('fouridentity.urls')),
    path('vol/', include('vol.urls')),
    path('oneshot/', include('oneshot.urls')),
    path('webhook/', include('webhook.urls')),
    path('eSignAnyWhere/', include('eSignAnyWhere.urls')),
    path('planilla/', include('pagoplanilla.urls')),
    path('flujo_firma/', include('flujofirma.urls')),
    path('silk/', include('silk.urls', namespace='silk')),
] 

# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.FORCE_STATIC_FILE_SERVING and not settings.DEBUG:
#     settings.DEBUG = True
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     settings.DEBUG = False
    
    


