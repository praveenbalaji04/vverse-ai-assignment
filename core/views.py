import os
import secrets
import logging
import cv2 as cv

from core.models import Video
from core.helpers import TrimVideo

from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser


logger = logging.getLogger(__name__)


@api_view(["GET"])
@authentication_classes([])
def health_check(request):
    return Response({"status": "ok"})


class UploadVideoAPI(APIView):
    parser_classes = [MultiPartParser]
    # token authentication is added as default authentication in settings.py

    def _validate_size(self, file_size: int):
        min_size = 5 * 1024 * 1024  # min of 5 MB
        max_size = 25 * 1024 * 1024  # max of 25 MB

        if min_size <= file_size <= max_size:
            return True
        return False

    def _validate_duration(self, cv_video):
        fps = cv_video.get(cv.CAP_PROP_FPS)
        frame_count = cv_video.get(cv.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps

        if 5 <= duration <= 35:  # TODO change this to 25
            return True
        return False

    def post(self, request):
        """
        payload:
            file: video-file

        validation:
            - file size: 5 < 25mb
            - file length: 5 < 25 seconds
        """

        video_file = request.FILES.get("video_file")
        if not video_file:
            raise ValidationError({"error": "video_file is required"})

        if not self._validate_size(video_file.size):
            return Response(
                {"error": "Video size should be between 5MB and 25 MB"},
                status=status.HTTP_417_EXPECTATION_FAILED
            )

        file_path = os.path.join(settings.MEDIA_ROOT, video_file.name)
        logger.info(f"saving file to media folder with filename {video_file.name}")
        with open(file_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)
        logger.info(f"completed saving file to media folder with filename {video_file.name}")

        cv_video = cv.VideoCapture(file_path)
        if cv_video.isOpened():
            if not self._validate_duration(cv_video):
                return Response(
                    {"error": "Video length should be less than 25 seconds"},
                    status=status.HTTP_417_EXPECTATION_FAILED
                )
        else:
            raise ValidationError({"error": "Invalid video file"})

        logger.info(f"creating video object for filename {video_file.name}")
        Video.objects.create(file=video_file, name=video_file.name)

        self.delete_local_file(file_path)
        logger.info(f"deleted locally created file with filename {video_file.name}")

        return Response({"status": "created"}, status=status.HTTP_201_CREATED)

    def delete_local_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)


class TrimVideoView(APIView):

    def post(self, request, video_id):
        """
        payload: {start: <int>, end: <int>}
        """
        data = request.data
        start = data.get("start")
        end = data.get("end")

        if not isinstance(start, int) or not isinstance(end, int):
            raise ValidationError({"error": "start and end is mandatory and should be integer"})

        if start > end:
            raise ValidationError({"error": "start should be less than end"})

        logger.info(f"trimming video with id: {video_id}, requested by user")
        video_obj = Video.objects.get(id=video_id)  # if user is available, make sure video belongs to user.
        cv_video = cv.VideoCapture(video_obj.file.path)

        if cv_video.isOpened():
            video_file_name = video_obj.name.split(".")[0]
            output_path = os.path.join(settings.MEDIA_ROOT, f"trimmed_{video_file_name}_{str(secrets.token_hex(3))}.mp4")
            logger.info(f"creating trimmed video with filename {output_path}")

            trim_video = TrimVideo(video_obj, start, end, output_path)
            try:
                trim_video.execute()
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            raise ValidationError({"error": "Invalid video file"})
        return Response({"status": "trimmed"})

