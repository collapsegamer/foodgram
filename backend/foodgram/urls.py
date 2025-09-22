from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve
from django.conf import settings
from shortener.views import redirect_short_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:code>/', redirect_short_link, name='short-link'),

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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT
                          )
