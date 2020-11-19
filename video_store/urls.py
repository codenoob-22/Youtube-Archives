from django.contrib import admin
from django.urls import path, include

from video_store.views import VideoRoute, APIKeyRoute

urlpatterns = [
    path('search/', include(VideoRoute.urls)),
    path('youtube_keys/', include(APIKeyRoute.urls)),
]
