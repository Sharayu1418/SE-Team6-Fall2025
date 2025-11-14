# downloader/views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DownloadedContent
from .serializers import DownloadedContentSerializer, CreateDownloadTaskSerializer
from .services import download_media
import threading

class DownloadAPIView(APIView):
    def post(self, request):
        serializer = CreateDownloadTaskSerializer(data=request.data)
        if serializer.is_valid():
            url = serializer.validated_data['url']
            download_type = serializer.validated_data['type']

            # Create the record with the specified type
            content_instance = DownloadedContent.objects.create(
                source_url=url,
                requested_type=download_type
            )
            
            # Trigger the download in the background
            thread = threading.Thread(target=download_media, args=(content_instance.id,))
            thread.start()

            response_serializer = DownloadedContentSerializer(content_instance)
            return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, task_id=None):
        """
        Get download task status by ID.
        URL: /api/download/<task_id>/
        """
        try:
            content_instance = DownloadedContent.objects.get(id=task_id)
            response_serializer = DownloadedContentSerializer(content_instance)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        except DownloadedContent.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid task ID format'},
                status=status.HTTP_400_BAD_REQUEST
            )