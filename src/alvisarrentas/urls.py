"""alvisarrentas URL Configuration
"""
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^users/', include('django.contrib.auth.urls')),

    url(r'^', include('webapp.urls', namespace='webapp')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
