import logging
import cv2 as cv
from dataclasses import dataclass
from core.models import Video


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


class MergeVideo:
    def __init__(self, video_objects, output_path, video_ids):
        self.video_objects = video_objects
        self.output_path = output_path
        self.video_ids = video_ids

    def get_frame_info(self):

        logger.info("fetching frame info for video to merge videos")
        cv_video = cv.VideoCapture(self.video_objects.first().file.path) # using first video property for all videos
        fps = cv_video.get(cv.CAP_PROP_FPS)
        width = int(cv_video.get(cv.CAP_PROP_FRAME_WIDTH))
        height = int(cv_video.get(cv.CAP_PROP_FRAME_HEIGHT))

        cv_video.release()

        frame_info = FrameInfo()
        frame_info.fps = fps
        frame_info.width = width
        frame_info.height = height

        return frame_info

    def execute(self):
        frame_info = self.get_frame_info()
        fourcc = cv.VideoWriter_fourcc(*'mp4v')
        out = cv.VideoWriter(self.output_path, fourcc, frame_info.fps, (frame_info.width, frame_info.height))

        video_objects_path = {video.id: video.file.path for video in self.video_objects}
        for _id in self.video_ids:  # making sure videos are fetched as per requested order
            video_obj_path = video_objects_path.get(_id)
            cv_video = cv.VideoCapture(video_obj_path)
            logger.info(f"reading video file for merge. video_id: {_id}")

            while True:
                ret, frame = cv_video.read()
                if not ret:
                    break

                frame = cv.resize(frame, (frame_info.width, frame_info.height))
                out.write(frame)
            cv_video.release()

        out.release()
