from django.db import models
from django.db.models import CharField, TextField, DateTimeField, IntegerField, BooleanField
from django.db.models import Q
# Create your models here.
import logging

logger = logging.getLogger("process_log")

class Video(models.Model):
    title           = CharField(max_length=200, db_index=True, help_text="video title")
    description     = TextField(default='', db_index=True)
    youtube_id      = CharField(max_length=20, unique=True, help_text="videoId")
    published_at  = DateTimeField()

    def __str__(self):
        return f"{self.youtube_id}-{self.title}"

    @property
    def thumbnail(self):
        ''' since yt thumbnails are stored with this address, so 
            not storing it in database rather retrieving from youtube_id
        '''
        return f"https://i.ytimg.com/vi/{self.youtube_id}/mqdefault.jpg"

    @staticmethod
    def search_videos_with_keywords(keywords):
        # cache_key = '_'.join(sorted(keywords))
        title_query = Q()
        description_query = Q()
        queryset = Video.objects.all()
        
        for keyword in keywords:
            # we are making nexxesary that all kywords should be contained either in
            # title or description 
            title_query &= Q(title__icontains=keyword)
            description_query &= Q(description__icontains=keyword)
        
        query = title_query | description_query 
        if query:
            queryset = Video.objects.filter(query)
        
        return queryset

class APIKey(models.Model):
    '''  model to store youtube API keys'''
    api_key             = CharField(max_length=200, unique=True, help_text="api key of youtube API") 
    quota_available     = BooleanField(default=True, help_text="check whether quota is finished, update to false")
    last_used           = DateTimeField()

    def __str__(self):
        return self.api_key
    
class RemainingJobs(models.Model):
    ''' 
        Model to store failed jobs due to quota exhaustion
        - there was one observation, even with same page_token the values were changing
        , and when i kept upper and lower bound on publishedAt it became constant.
        - tasks would make sure that lower and upper bound of one entry does not 
        intersect with any other entry. 
    '''
    page_token          = CharField(max_length=20, unique=True, help_text="storing next page token so we can continue"
                                                             " with the paginated results")
    lower_date_bound    = DateTimeField(help_text="storing the lower bound of date so that i can filter using after query")
    upper_date_bound    = DateTimeField(help_text="storing upper bound so we know that our list is between the bounds")