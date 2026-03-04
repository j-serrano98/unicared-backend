from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='admin/', permanent=True)),
    path('admin/', admin.site.urls),
    path('api/v1/', include('teachers.urls')),
]
