import pytz
from datetime import datetime

from django.shortcuts import render
from rest_framework import mixins, viewsets, serializers
from rest_framework.routers import DefaultRouter
from rest_framework.pagination import PageNumberPagination

from video_store.models import Video, APIKey, RemainingJobs
import logging
# Create your views here.

logger = logging.getLogger("process_log")

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ("title", "youtube_id", "published_at", "thumbnail", "description")
    

class VideoView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = VideoSerializer

    def get_queryset(self):
        search_query = self.request.query_params.get('search_query', '')
        keywords = [i for i in search_query.split(' ') if i != '']
        return Video.search_videos_with_keywords(keywords)

VideoRoute = DefaultRouter()
VideoRoute.register(r'', VideoView, basename='video')


class APIkeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ("id", "api_key", "quota_available", "last_used")
        extra_kwargs = {
            "last_used": { "read_only": True},
            "quota_available": { "read_only" : True}
        }
    

class APIKeyView(viewsets.ModelViewSet):
    serializer_class = APIkeySerializer
    queryset = APIKey.objects.all().order_by('-last_used')


APIKeyRoute = DefaultRouter()
APIKeyRoute.register(r'', APIKeyView, basename='api_key')