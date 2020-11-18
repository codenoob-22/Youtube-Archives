import pytz
from datetime import datetime, timezone, timedelta


from video_store.models import Video, APIKey, RemainingJobs
from video_store.platforms import YouTube


import logging
logger = logging.getLogger("background_jobs")


SEARCH_TERM = "medical"

def add_videos_to_db():
    ''' task for fetching videos and put it into DB '''
    UTC = pytz.timezone('UTC')
    try:
        latest_published_date = Video.objects.all().ordered_by('-published_at').first().published_at
    except AttributeError:
        #in case there is no video we are fetching videos published just one second ago :D 
        latest_published_date = datetime.now(UTC) - timedelta(seconds=1)
    api_key = APIKey.get_api_key()
    y = YouTube(api_key)
    global SEARCH_TERM
    response = y.get_video_results(SEARCH_TERM, published_after=latest_published_date)

    if response['status'] = 'error':
        ''' 
            can be two cases if it fails at first go, we will calculate it in next round otherwise we 
            store it in the remaining jobs.
        '''
        video_data = response['video_data']
        if video_data:
            upper_bound = video_data[0]['published_at']    
            r = RemainingJobs.objects.create(page_token=response['page_token'], 
                                        lower_date_bound=latest_published_date,
                                        upper_date_bound=upper_bound)
        
        APIKey.set_status_to_exhausted(api_key)
    video_data = response['video_data']
    videos = [Video(**data) for data in video_data]
    Video.objects.bulk_create(videos)

def complete_remaining_jobs():
    ''' taking up the least recent job and finishing it '''
    job = RemainingJobs.objects.all().order_by('lower_date_bound').first()
    if job:
        api_key = APIKey.get_api_key()
        y = YouTube(api_key)

        global SEARCH_TERM
        response = y.get_video_results(SEARCH_TERM, 
                                       published_after=job.lower_date_bound, 
                                       published_before=job.upper_date_bound)

        if response['status'] = 'error':
            ''' 
                can be two cases if it fails at first go, we will calculate it in next round otherwise we 
                store it in the remaining jobs.
            '''
            video_data = response['video_data']
            # check if page_token is not null, otherwise we can lose our progress track
            if video_data and response['page_token']:
                job.page_token = response['page_token']  
                job.save() 
            
            APIKey.set_status_to_exhausted(api_key)
        video_data = response['video_data']
        videos = [Video(**data) for data in video_data]
        Video.objects.bulk_create(videos)


def refresh_keys():
    UTC = pytz.timezone('UTC')
    refresh_time = datetime.now(UTC) - timedelta(days=1, minutes=1)
    APIKey.objects.filter(quota_available=False, last_used__lte=refresh_time).update(quota_available=True)