from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from propylon_document_manager.users.api.views import UserViewSet
from propylon_document_manager.file_versions.api.views import FileVersionViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("file_versions", FileVersionViewSet, basename='file_versions')


app_name = "api"
urlpatterns = router.urls
