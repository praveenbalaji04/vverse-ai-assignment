import secrets
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from core.tests import STATIC_HEADER, create_mock_video, delete_files
from core.models import Video

from django.urls import reverse


class MergeVideosTestCase(APITestCase):
    def setUp(self) -> None:
        self.url = reverse("merge_video_api")

    def test_001_invalid_payload(self):
        response = self.client.post(self.url, {}, format='json', headers=STATIC_HEADER)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_json = response.json()

        self.assertEqual(response_json.get("error"), "video_ids should be a list of integers")

    def test_002_less_than_2_video_ids(self):
        payload = {"video_ids": [1]}
        response = self.client.post(self.url, payload, format='json', headers=STATIC_HEADER)
        self.assertEqual(response.status_code, status.HTTP_412_PRECONDITION_FAILED)
        response_json = response.json()

        self.assertEqual(response_json.get("error"), "at least 2 video_ids are required")

    def test_003_invalid_video_ids(self):
        payload = {"video_ids": [100, 101]}
        response = self.client.post(self.url, payload, format='json', headers=STATIC_HEADER)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_json = response.json()

        self.assertEqual(response_json.get("error"), "Invalid video_ids")

    def test_004_merge_video_ids(self):
        # create 5 mock videos to merge
        url = reverse("upload_video_api")
        for _ in range(0, 3):
            mock_video_path = create_mock_video(duration=15, size=(3840, 2160), frame_rate=40)

            with open(mock_video_path, 'rb') as mock_video_file:
                # Create a SimpleUploadedFile object
                uploaded_video = SimpleUploadedFile(
                    name=f"mock_video_{secrets.token_hex(3)}.mp4",
                    content=mock_video_file.read(),
                    content_type="video/mp4"
                )
                payload = {
                    'video_file': uploaded_video,
                }
                response = self.client.post(url, payload, format='multipart', headers=STATIC_HEADER)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        video_ids = Video.objects.values_list('id', flat=True)
        payload = {"video_ids": list(video_ids)}

        response = self.client.post(self.url, payload, format='json', headers=STATIC_HEADER)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()

        self.assertEqual(response_json.get("status"), "completed")

        self.assertIn("merged_", response_json.get("output_path"))
        self.assertIn(".mp4", response_json.get("output_path"))

    @classmethod
    def tearDownClass(cls) -> None:
        delete_files()
