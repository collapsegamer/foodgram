from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('api/docs/',
         TemplateView.as_view(template_name='redoc.html'), name='redoc'),
    path(
        'api/openapi-schema.yml',
        serve,
        {'path': 'openapi-schema.yml',
         'document_root': settings.BASE_DIR / 'templates'},
        name='openapi-schema'
    ),
]
