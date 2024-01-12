from django.db import models
from django.utils import timezone
from propylon_document_manager.users import models as user_models

# from django.contrib.auth.models import User


class FileVersion(models.Model):
    file_name = models.fields.CharField(max_length=512)
    version_number = models.fields.IntegerField(default=0)
    owned_by = models.ForeignKey(user_models.User, on_delete=models.DO_NOTHING, default=1)
    created_on = models.DateTimeField(blank=False, null=True, default=timezone.now)
    file_url = models.TextField(blank=False, null=True, default=None)
    file_binary = models.BinaryField(null=True, default=None)
#     owned/file_url/file_name

