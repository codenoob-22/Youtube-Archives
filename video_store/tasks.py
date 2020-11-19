import pytz
from datetime import datetime, timezone, timedelta


from video_store.models import Video, APIKey, RemainingJobs
from video_store.platforms import YouTube


import logging
logger = logging.getLogger("background_jobs")


SEARCH_TERM = "medical"

def fetch_and_add_videos_to_db():
    ''' task for fetching videos and put it into DB '''
    UTC = pytz.timezone('UTC')
    try:
        latest_published_date = Video.objects.all().order_by('-published_at').first().published_at
    except AttributeError:
        #in case there is no video we are fetching videos published last 1 hour 
        latest_published_date = datetime.now(UTC) - timedelta(hours=1)
    api_key = APIKey.get_api_key()
    y = YouTube(api_key)
    global SEARCH_TERM
    response = y.get_video_results(SEARCH_TERM, published_after=latest_published_date)

    if response['status'] == 'error':
        ''' 
            can be two cases if it fails at first go, we will calculate it in next round otherwise we 
            store it in the remaining jobs.
        '''
        video_data = response['video_data']
        if video_data and response.get('page_token'):
            upper_bound = video_data[0]['published_at']    
            RemainingJobs.add_job(response['page_token'], upper_bound, latest_published_date, response['reason'])

    video_data = response['video_data']
    Video.store_to_db(video_data)

def complete_remaining_jobs():
    ''' taking up the least recent job and finishing it '''
    job = RemainingJobs.get_oldest_job()
    if not job:
        return

    api_key = APIKey.get_api_key()
    y = YouTube(api_key)

    global SEARCH_TERM
    response = y.get_video_results(SEARCH_TERM, 
                                    published_after=job.lower_date_bound, 
                                    published_before=job.upper_date_bound)

    if response['status'] == 'error':
        video_data = response['video_data']
        # check if page_token is not null, otherwise we can lose our progress track
        if response.get('page_token'):
            job.page_token = response['page_token']  
            job.save()
    
    if response['status'] == 'success':
        job.delete()
    video_data = response['video_data']
    Video.store_to_db(video_data)
        


def refresh_keys():
    UTC = pytz.timezone('UTC')
    refresh_time = datetime.now(UTC) - timedelta(days=1, minutes=1)
    APIKey.objects.filter(quota_available=False, last_used__lte=refresh_time).update(quota_available=True)