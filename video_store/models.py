
from datetime import datetime, timedelta

from django.db import models
from django.db.models import CharField, TextField, DateTimeField, IntegerField, BooleanField
from django.db.models import Q
from asgiref.sync import sync_to_async
from django.utils import timezone
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
        ''' using static address for retrieving thumbnails
        '''
        return f"https://i.ytimg.com/vi/{self.youtube_id}/mqdefault.jpg"
    # @sync_to_async
    @staticmethod
    def search_videos_with_keywords(keywords):
        # cache_key = '_'.join(sorted(keywords))
        title_query = Q()
        description_query = Q()
        queryset = Video.objects.all().order_by('-published_at')
        
        for keyword in keywords:
            # we are making neccesary that all keywords should be contained either in
            # title or description 
            title_query &= Q(title__icontains=keyword)
            description_query &= Q(description__icontains=keyword)
        
        query = title_query | description_query 
        if query:
            queryset = Video.objects.filter(query).order_by('-published_at')
        
        return queryset
    
    @staticmethod
    def store_to_db(video_data):
        ''' method for storing video data along with handling duplication of any video '''
        youtube_ids = [v['youtube_id'] for v in video_data]
        existing_youtube_ids = Video.objects.filter(youtube_id__in=youtube_ids).values_list('youtube_id', flat=True)
        videos = [Video(**data) for data in video_data \
                    if data['youtube_id'] not in existing_youtube_ids \
                    and data['youtube_id']]

        Video.objects.bulk_create(videos)
        logger.info(f"{len(videos)} video/s have been added to database")

class APIKey(models.Model):
    '''  model to store youtube API keys'''
    api_key             = CharField(max_length=200, unique=True, help_text="api key of youtube API") 
    quota_available     = BooleanField(default=True, help_text="check whether quota is finished, update to false")
    last_used           = DateTimeField(default=timezone.now)

    def __str__(self):
        return self.api_key
    
    # @sync_to_async
    @staticmethod
    def get_api_key():
        # using the one which is least recently used
        least_recent_apikey = APIKey.objects.filter(quota_available=True).order_by('last_used').first()
        if not least_recent_apikey:
            logger.exception("FATAL: active API keys do not exist!!!!")
            raise ValueError("we are exhausted on API keys")
        least_recent_apikey.last_used = timezone.now()
        least_recent_apikey.save()
        return least_recent_apikey.api_key

    # @sync_to_async
    @staticmethod
    def set_status_to_exhausted(api_key):
        logger.info(f'{api_key} got exhausted')
        APIKey.objects.filter(api_key=api_key).update(quota_available=False, last_used=timezone.now())
    
class RemainingJobs(models.Model):
    ''' 
        Model to store failed jobs due to some reasons
        - there was one observation, even with same page_token the values were changing
        , and when i kept upper and lower bound on publishedAt it became constant.
        - tasks would make sure that lower and upper bound of one entry does not 
        intersect with any other entry. 
    '''
    page_token          = CharField(max_length=20, help_text="storing next page token so we can continue"
                                                             " with the paginated results")
    lower_date_bound    = DateTimeField(help_text="storing the lower bound of date so that i can filter using after query")
    upper_date_bound    = DateTimeField(help_text="storing upper bound so we know that our list is between the bounds")
    reason_for_failure  = TextField(default='', help_text="can be used for analysis of errors") 

    # @sync_to_async
    @staticmethod
    def add_job(page_token, upper_bound, lower_bound, reason):
        job = RemainingJobs.objects.create(
            page_token          = page_token,
            upper_date_bound    = upper_bound,
            lower_date_bound    = lower_bound,
            reason_for_failure  = reason,
        )
    
    @staticmethod
    def get_oldest_job():
        oldest_job = RemainingJobs.objects.all().order_by('lower_date_bound').first()
        return oldest_job