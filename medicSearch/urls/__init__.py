from .HomeUrls import urlpatterns as home_urlpatterns
from .ProfileUrls import urlpatterns as profile_urlpatterns
from .MedicUrls import urlpatterns as medic_urlpatterns
from .AuthUrls import urlpatterns as auth_urlpatterns

# Habilita customizar a URL principal para (path('', include('medicSearch.urls')))
urlpatterns = home_urlpatterns
urlpatterns = profile_urlpatterns
urlpatterns = medic_urlpatterns
urlpatterns = auth_urlpatterns
