from django.urls import path

from core.views import (
    health_check,
    UploadVideoAPI,
    TrimVideoView,
    MergeVideoView,
    FileLinkWithExpiryView,
)


urlpatterns = [
    path("health/", health_check, name="health_check"),
    path("video/upload/", UploadVideoAPI.as_view(), name="upload_video_api"),
    path("video/trim/<int:video_id>/", TrimVideoView.as_view(), name="trim_video_api"),
    path("video/merge/", MergeVideoView.as_view(), name="merge_video_api"),
    path("video/link/<int:video_id>/", FileLinkWithExpiryView.as_view(), name="file_link_with_expiry"),
]
