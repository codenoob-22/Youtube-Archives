import json
import requests
from dateutil import parser
from urllib.parse import urlencode

import google_auth_oauthlib.flow
import googleapiclient

from django.conf import settings

import logging

logger = logging.getLogger("process_log")


class YouTube:
    ''' class implements all Youtube API interactions '''
    def __init__(self, apikey):
        self.url = f"{settings.YOUTUBE_API_URL}key={apikey}" 
    
    def get_video_results(self, search_term, published_after=None, page_token=None, published_before=None):

        if not published_after:
            raise ValueError("please provide published_after")
        query_params={
            "publishedAfter": published_after,
            "q": search_term,
            "relevanceLanguage": "EN",
            "regionCode": "IN",
            "order": "date"
        }

        if published_before:
            query_params['publishedBefore'] = published_before

        self.url += '&' + urlencode(query_params)
        url = self.url
        if page_token:
            url += '&' + urlencode({'pageToken': page_token})

        response = requests.get(url)
        data = json.loads(response.text)
        try:
            assert response.status_code == 200
        except AssertionError:
            return {
                    'status': 'error',
                    'video_data': [],
                    'page_token': None,
                }

        video_data = []

        while data['nextPageToken']:
            for item in data['items']:

                video_data_dict = {
                    'youtube_id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'published_at': parser.parse(item['snippet']['publishedAt']),
                }

                video_data.append(video_data_dict)
            try:
                url = self.url + '&' + urlencode({'pageToken': data['nextPageToken']})
                response = requests.get(url)
                assert response.status_code == 200
                data = json.loads(response.text)
            except AssertionError:
                return {
                        'status': 'error', 
                        'video_data': video_data, 
                        'page_token': data['nextPageToken'],
                        }
        
        return {
            'status': 'success', 
            'video_data': video_data,
        }

