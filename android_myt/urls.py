from django.urls import path
from . import views

app_name = 'android_myt'

urlpatterns = [
    path('post-video/', views.post_video, name='post_video'),
    path('scroll-videos/', views.scroll_videos, name='scroll_videos'),
    path('get-video-data/', views.get_video_data, name='get_video_data'),
]