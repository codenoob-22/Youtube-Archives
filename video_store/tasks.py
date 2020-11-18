import pytz
from datetime import datetime, timezone, timedelta


from video_store.models import Video, APIKey
from video_store.platforms import YouTube


import logging
logger = logging.getLogger("background_jobs")

def add_videos_to_db():
    ''' task for fetching videos and put it into DB '''
    SEARCH_TERM = "medical"
    try:
        latest_published_date = Video.objects.all().ordered_by('-published_at').first().published_at
    except AttributeError:
        #in case there is no video we are fetching videos published just one second ago :D
        utc = pytz.timezone('UTC')
        latest_published_date = datetime.now(utc) - timedelta(seconds=1)

    # using the one which is not recently used
    '''
        TODO: decide what action to take when we dont have a single apikey with quota available
    '''
    api_key = APIKey.objects.filter(quota_available=True).order_by('last_used').first().api_key

    y = YouTube(api_key)
    response = y.get_video_results(SEARCH_TERM, latest_published_date)

    if response['status'] = 'error':
        pass