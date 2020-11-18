from django.db import models
from django.db.models import CharField, DateTimeField, IntegerField, BooleanField
from django.db.models import Q
# Create your models here.
import logging

logger = logging.getLogger("process_log")

class Video(models.Model):
    title           = CharField(max_length=200, help_text="video title")
    youtube_id      = CharField(max_length=20, unique=True, help_text="videoId")
    published_date  = DateTimeField()

    def __str__(self):
        return f"{self.youtube_id}-{self.title}"

    @staticmethod
    def search_videos_with_keywords(keywords):
        # cache_key = '_'.join(sorted(keywords))
        query = Q()
        queryset = None
        for keyword in keywords:
            query &= Q(title__icontains=keyword)
        if query:
            queryset = Video.objects.filter(query)
        
        return queryset

class APIKey(models.Model):
    '''  model to store youtube API keys'''
    api_key             = CharField(max_length=200, help_text="api key of youtube API") 
    quota_available     = BooleanField(default=True, help_text="check whether quota is finished, update to false")
    last_status_updated = DateTimeField()

    def __str__(self):
        return self.api_key
    
