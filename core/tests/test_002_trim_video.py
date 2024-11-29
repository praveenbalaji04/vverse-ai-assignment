import os

from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from core.tests import STATIC_HEADER, create_mock_video, delete_files
from core.models import Video

from django.urls import reverse


class TrimVideoTestCase(APITestCase):

    def test_001_invalid_payload(self):
        url = reverse("trim_video_api", args=[1])

        response = self.client.post(url, {}, format='json', headers=STATIC_HEADER)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_json = response.json()

        self.assertEqual(response_json.get("error"), "start and end is mandatory and should be integer")

    def test_002_mismatch_start_end(self):
        url = reverse("trim_video_api", args=[1])

        payload = {"start": 10, "end": 5}
        response = self.client.post(url, payload, format='json', headers=STATIC_HEADER)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_json = response.json()

        self.assertEqual(response_json.get("error"), "start should be less than end")

    def test_003_invalid_video_id(self):
        url = reverse("trim_video_api", args=[100])

        payload = {"start": 10, "end": 15}
        response = self.client.post(url, payload, format='json', headers=STATIC_HEADER)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response_json = response.json()

        self.assertEqual(response_json.get("detail"), "Video does not exist")

    def test_004_trim_video(self):
        # create video to trim
        mock_video_path = create_mock_video(duration=15, size=(3840, 2160), frame_rate=60)

        with open(mock_video_path, 'rb') as mock_video_file:
            # Create a SimpleUploadedFile object
            url = reverse("upload_video_api")
            uploaded_video = SimpleUploadedFile(
                name="mock_video.mp4",
                content=mock_video_file.read(),
                content_type="video/mp4"
            )
            payload = {
                'video_file': uploaded_video,
            }
            response = self.client.post(url, payload, format='multipart', headers=STATIC_HEADER)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        video_id = Video.objects.last().id
        url = reverse("trim_video_api", args=[video_id])

        payload = {"start": 5, "end": 12}
        response = self.client.post(url, payload, format='json', headers=STATIC_HEADER)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()

        self.assertEqual(response_json.get("status"), "completed")

        path = response_json.get("output_path")
        self.assertTrue(path is not None and os.path.exists(path))

    @classmethod
    def tearDownClass(cls) -> None:
        delete_files()
