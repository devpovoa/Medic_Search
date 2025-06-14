from .HomeUrls import urlpatterns as home_urlpatterns
from .ProfileUrls import urlpatterns as profile_urlpatterns
# Habilita customizar a URL principal para (path('', include('medicSearch.urls')))
urlpatterns = home_urlpatterns
urlpatterns = profile_urlpatterns
