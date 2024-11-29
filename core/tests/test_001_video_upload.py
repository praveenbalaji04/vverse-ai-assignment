import os
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from core.tests import create_mock_video, STATIC_HEADER, delete_files
from core.models import Video

from django.urls import reverse


class VideoUploadTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("upload_video_api")

    def test_001_video_upload_without_video_file(self):

        response = self.client.post(self.url, {}, format='multipart', headers=STATIC_HEADER)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_json = response.json()
        self.assertEqual(response_json.get("error"), "video_file is required")

    def test_002_video_upload_longer_duration_video(self):

        mock_video_path = create_mock_video(duration=45, size=(1920, 1080))

        with open(mock_video_path, 'rb') as mock_video_file:
            # Create a SimpleUploadedFile object
            uploaded_video = SimpleUploadedFile(
                name="mock_video.mp4",
                content=mock_video_file.read(),
                content_type="video/mp4"
            )
            payload = {
                'video_file': uploaded_video,
            }

            response = self.client.post(self.url, payload, format='multipart', headers=STATIC_HEADER)

        self.assertEqual(response.status_code, status.HTTP_417_EXPECTATION_FAILED)
        response_json = response.json()
        self.assertEqual(response_json.get("error"), "Video length should be less than 25 seconds")

    def test_003_video_upload_large_size_video(self):
        mock_video_path = create_mock_video(duration=24, size=(3840, 2160), frame_rate=90)

        with open(mock_video_path, 'rb') as mock_video_file:
            # Create a SimpleUploadedFile object
            uploaded_video = SimpleUploadedFile(
                name="mock_video.mp4",
                content=mock_video_file.read(),
                content_type="video/mp4"
            )
            payload = {
                'video_file': uploaded_video,
            }

            response = self.client.post(self.url, payload, format='multipart', headers=STATIC_HEADER)

        self.assertEqual(response.status_code, status.HTTP_417_EXPECTATION_FAILED)
        response_json = response.json()
        self.assertEqual(response_json.get("error"), "Video size should be between 5MB and 25 MB")

    def test_004_video_upload(self):
        mock_video_path = create_mock_video(duration=15, size=(3840, 2160), frame_rate=60)

        with open(mock_video_path, 'rb') as mock_video_file:
            # Create a SimpleUploadedFile object
            uploaded_video = SimpleUploadedFile(
                name="mock_video.mp4",
                content=mock_video_file.read(),
                content_type="video/mp4"
            )
            payload = {
                'video_file': uploaded_video,
            }

            response = self.client.post(self.url, payload, format='multipart', headers=STATIC_HEADER)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response_json = response.json()
        self.assertEqual(Video.objects.count(), 1)
        self.assertEqual(response_json.get("status"), "created")

    @classmethod
    def tearDownClass(cls) -> None:
        delete_files()
