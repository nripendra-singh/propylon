from rest_framework import serializers

from file_versions.models import FileVersion

class FileVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileVersion
        fields = ['file_name', 'version_number', 'owned_by', 'created_on', 'file_url', 'file_binary']


