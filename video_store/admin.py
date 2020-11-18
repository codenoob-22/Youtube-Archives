from django.contrib import admin
from video_store.models import Video, APIKey
# Register your models here.

admin.site.register(Video)
admin.site.register(APIKey)