from django.urls import path

from core.views import (
    health_check,
    UploadVideoAPI,
    TrimVideoView,
)


urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("video/upload/", UploadVideoAPI.as_view(), name="upload_video_api"),
    path("video/trim/<str:video_id>/", TrimVideoView.as_view(), name="trim_video_api"),
]