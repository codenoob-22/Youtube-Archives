from django.shortcuts import render
from rest_framework import mixins, viewsets, serializers
from rest_framework.routers import DefaultRouter
from rest_framework.pagination import PageNumberPagination

class SetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'length'
    max_page_size = 100

from video_store.models import Video
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
VideoRoute.register(r'', VideoView, basename='video-search')