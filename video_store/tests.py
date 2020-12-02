from datetime import datetime, timezone, timedelta

from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils import timezone
from sqlite3 import IntegrityError as sqlite3Error

from video_store.models import Video, APIKey, RemainingJobs

# Create your tests here.

class VideoAPITest(TestCase):
    
    def test_createvideo(self):
        Video.objects.create(youtube_id='1234', title='asda', description='asdasd', published_at=datetime.now())
        assert True
    
    def test_createapikey(self):
        APIKey.objects.create(api_key='asdaosdimo')
        assert True


class APIKeyTest(TestCase):

    def test_when_all_keys_exhaust(self):
        APIKey.objects.create(api_key="wwiefowifoewf", quota_available=False)
        self.assertRaises(ValueError, APIKey.get_api_key)


class RemainingJobTest(TestCase):

    def test_remaining_job(self):
        s = RemainingJobs.get_oldest_job()
        assert s is None, "should be none, since no job was created"
    
    def test_remaining_job_queue(self):
        s = RemainingJobs.objects.create(lower_date_bound=timezone.now() - timedelta(hours=2), upper_date_bound=timezone.now(), reason_for_failure="nope")
        x = RemainingJobs.objects.create(lower_date_bound=timezone.now() - timedelta(hours=1), upper_date_bound=timezone.now(), reason_for_failure="nope")
        assert RemainingJobs.get_oldest_job() == s, "should be oldest job in the queue"
    
    
    def test_create_invalid_job(self):
        def tester():
            RemainingJobs.objects.create(lower_date_bound=timezone.now() - timedelta(hours=1), upper_date_bound=timezone.now() - timedelta(hours=2), reason_for_failure="nope")
        self.assertRaises(IntegrityError, tester)