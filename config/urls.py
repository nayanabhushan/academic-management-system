from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import user_login

urlpatterns = [
    path("", user_login, name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("student/", include("student.urls")),
    path("teacher/", include("teacher.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )