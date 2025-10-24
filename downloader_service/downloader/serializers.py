from rest_framework import serializers
from .models import DownloadedContent

class DownloadedContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadedContent
        fields = '__all__'
        read_only_fields = ('status', 'content_file', 'title', 'content_type', 'metadata')

class CreateDownloadTaskSerializer(serializers.Serializer):
    url = serializers.URLField(max_length=1024)
    type = serializers.ChoiceField(choices=DownloadedContent.DownloadType.choices)