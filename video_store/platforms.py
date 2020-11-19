import json
import requests
from dateutil import parser
from urllib.parse import urlencode

import google_auth_oauthlib.flow
import googleapiclient

from django.conf import settings
from video_store.models import APIKey

import logging

logger = logging.getLogger("process_log")


class YouTube:
    ''' class implements all Youtube API interactions '''
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = f"{settings.YOUTUBE_API_URL}key={self.api_key}"
        logger.info(f"got apikey as " + self.api_key)

    def build_url_with_new_key(self, query_params):
        ''' when one key is exhausted, take another key from available keys'''
        APIKey.set_status_to_exhausted(self.api_key)
        self.api_key = APIKey.get_api_key()
        self.url = f"{settings.YOUTUBE_API_URL}key={self.api_key}&" + urlencode(query_params)
   
    def get_video_results(self, search_term, published_after=None, page_token=None, published_before=None):

        if not published_after:
            raise ValueError("argument missing `published_after`")

        query_params={
            "publishedAfter"    : published_after.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "q"                 : search_term,
            "relevanceLanguage" : "EN",
            "regionCode"        : "IN",
            "order"             : "date",
            "maxResults"        : 50,
            "part"              : "snippet",
        }
        logger.info(f"checking for published after- {published_after}")
        if published_before:
            query_params['publishedBefore'] = published_before.strftime('%Y-%m-%dT%H:%M:%SZ')
            logger.info(f" And published_before {published_before}")

        self.url += '&' + urlencode(query_params)
        url = self.url
        if page_token:
            url += '&' + urlencode({'pageToken': page_token})
        video_data = []
        count = 0
        
        while True:
            response = requests.get(url)
            data = json.loads(response.text)
            if response.status_code != 200:
                if response.status_code == 403:
                    try:
                        self.build_url_with_new_key(query_params)
                        if page_token:
                            url = self.url + urlencode({'pageToken': page_token}) 
                    except ValueError:
                        return {
                        'status'    : 'error',
                        'video_data': video_data,
                        'page_token': page_token,
                        'reason'    : "all keys have been exhausted",
                    }
                    continue
                else:
                    self.log_error_response(response)
                    return {
                        'status'    : 'error',
                        'video_data': video_data,
                        'page_token': page_token,
                        'reason'    : data["error"]["message"]
                    }
            for item in data['items']:
                video_data_dict = {
                    'youtube_id'    : item['id']['videoId'],
                    'title'         : item['snippet']['title'],
                    'published_at'  : parser.parse(item['snippet']['publishedAt']),
                    'description'   : item['snippet']['description']
                }
                video_data.append(video_data_dict)
            
            if not data['items'] or not data['nextPageToken']:
                logger.info(f"got end after {count} pages")
                break
            count += 1
            page_token = data['nextPageToken']
            url = self.url + '&' + urlencode({'pageToken': page_token})
        
        return {
            'status'    : 'success', 
            'video_data': video_data,
        }

    def log_error_response(self, response):
        logger.error('*' * 100)
        logger.error(f'got response status_code: - {response.status_code}')
        logger.error(response.text)
        logger.error('*' * 100)

