import secrets
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from core.tests import STATIC_HEADER, create_mock_video, delete_files
from core.models import Video

from django.urls import reverse


class FileLinkWithExpiryTestCase(APITestCase):

    def test_001_get_video_url_with_expiry(self):

        mock_video_path = create_mock_video(duration=15, size=(640, 480), frame_rate=30)  # small file to have faster test
        with open(mock_video_path, 'rb') as mock_video_file:
                # Create a SimpleUploadedFile object
                uploaded_video = SimpleUploadedFile(
                    name=f"mock_video_{secrets.token_hex(3)}.mp4",
                    content=mock_video_file.read(),
                    content_type="video/mp4"
                )
                
                Video.objects.create(name="testing_link", file=uploaded_video)

        video_id = Video.objects.last().id        
        url = reverse("file_link_with_expiry", args=[video_id])

        response = self.client.get(url, format='json', headers=STATIC_HEADER)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        self.assertEqual(response.headers.get("Cache-Control"), "public, max-age=10")
