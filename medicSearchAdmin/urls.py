from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
# Caso queira remover o HomeUrls, vai continuar funcionando.
    path('admin/', admin.site.urls),
    path('', include('medicSearch.urls.HomeUrls')),
    path('', include('medicSearch.urls.AuthUrls')),
    path('profile/', include('medicSearch.urls.ProfileUrls')),
    path('medics/', include('medicSearch.urls.MedicUrls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
