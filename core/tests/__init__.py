import os
import tempfile
import cv2
import numpy as np
from django.conf import settings

STATIC_HEADER = {"AUTH_TOKEN": "1534537f-f170-438f-b56a-58644a84233f"}

def create_mock_video(duration=10, size=(640, 480), frame_rate=30):
        """
        Create a mock video file for testing.
        """
        frame_width, frame_height = size
        test_media_dir = settings.TEST_MEDIA_ROOT
        file_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False, dir=test_media_dir).name

        # Define the codec and create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(file_path, fourcc, frame_rate, (frame_width, frame_height))

        for frame_num in range(frame_rate * duration):
            frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
            frame[:] = (255, 255, 255)  # White background
            center_x = (frame_num * 5) % frame_width
            center_y = frame_height // 2
            radius = 50
            color = (0, 255, 0)
            cv2.circle(frame, (center_x, center_y), radius, color, -1)
            out.write(frame)

        out.release()
        return file_path


def delete_files():
    dir_path = settings.TEST_MEDIA_ROOT
    for entry in os.listdir(dir_path):
        file_path = os.path.join(dir_path, entry)

        # Check if the entry is a file and remove it
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
