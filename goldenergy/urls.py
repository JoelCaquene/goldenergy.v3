from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Configuração para servir arquivos de Mídia (Comprovativos)
# Isso permite que o link /media/... funcione mesmo no Render (DEBUG=False)
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
else:
    # Em desenvolvimento local (DEBUG=True)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    