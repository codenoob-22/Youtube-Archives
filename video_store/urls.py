from django.contrib import admin
from django.urls import path, include

from video_store.views import VideoRoute

urlpatterns = [
    path('search/', include(VideoRoute.urls)),
]
