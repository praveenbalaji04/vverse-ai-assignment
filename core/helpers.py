import logging
import cv2 as cv
from dataclasses import dataclass
from core.models import Video


logger = logging.getLogger(__name__)


@dataclass
class FrameInfo:
    width: int = 0
    height: int = 0
    fps: int = 0
    start_frame: int = 0
    end_frame: int = 0


class TrimVideo:
    def __init__(self, video: Video, start: int, end: int, output_path):
        self.video = video
        self.start = start
        self.end = end
        self.output_path = output_path

        self.cv_video = cv.VideoCapture(video.file.path)
        self.file_name = video.name

    def fetch_frame_info(self):
        fps = self.cv_video.get(cv.CAP_PROP_FPS)
        total_frames = int(self.cv_video.get(cv.CAP_PROP_FRAME_COUNT))

        width = int(self.cv_video.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(self.cv_video.get(cv.CAP_PROP_FRAME_HEIGHT))

        start_frame = int(self.start * fps)  # convert seconds to frame
        end_frame = int(self.end * fps)
        end_frame = min(end_frame, total_frames - 1)

        frame_info = FrameInfo()
        frame_info.width = width
        frame_info.height = height
        frame_info.fps = fps
        frame_info.start_frame = start_frame
        frame_info.end_frame = end_frame

        return frame_info

    def execute(self):
        cv_video = cv.VideoCapture(self.video.file.path)

        if cv_video.isOpened():
            frame_info = self.fetch_frame_info()

            fourcc = cv.VideoWriter_fourcc(*'mp4v')
            out = cv.VideoWriter(self.output_path, fourcc, frame_info.fps, (frame_info.width, frame_info.height))
            cv_video.set(cv.CAP_PROP_POS_FRAMES, frame_info.start_frame)  # set the video to start frame

            while cv_video.isOpened():
                current_frame = int(cv_video.get(cv.CAP_PROP_POS_FRAMES))

                if current_frame > frame_info.end_frame:
                    break
                    
                ret, frame = cv_video.read()
                if not ret:
                    print("End of video or error reading frame.")
                    break

                out.write(frame)
                logger.info(f"writing frame {current_frame} to trimmed video, {self.output_path}")

            cv_video.release()
            out.release()
            logger.info(f"completed creating trimmed video with filename {self.output_path}")
