from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        "message": "Welcome to Unicared API",
        "status": "online",
        "endpoints": ["/admin/", "/teachers/"]
    })

urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/v1/', include('teachers.urls')),
]
