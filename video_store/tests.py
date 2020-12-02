from django.test import TestCase
from video_store.models import Video, APIKey
# Create your tests here.

def VideoAPITestCase(TestCase):
    
    def setUp(self):
        self.api_key = APIKey.objects.create(api_key='abcdefghi')
    
    def test_createvideo(self):
        Video.objects.create(youtube_id='1234', title='asda', description='asdasd')
        assert True
    
    def test_createapikey(self):
        APIKey.objects.create(api_key='asdaosdimo')
        assert True