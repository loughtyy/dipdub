
from django.contrib import admin
from django.urls import path, include
from store.admin import custom_admin_site

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('', include('store.urls')),
]

# To display images
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

