import threading
from abc import ABCMeta, abstractmethod, ABC
import cv2
import queue
import os

class VideoSource(metaclass=ABCMeta):
    """视频源的抽象类"""

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def copy(self):
        pass

    @abstractmethod
    def width(self):
        pass

    @abstractmethod
    def height(self):
        pass

    @abstractmethod
    def fps(self):
        pass

class VideoReader(VideoSource, ABC):
    """读取视频流"""

    def __init__(self, video_addr, enable_rtsp_over_tcp=False):
        self.video_addr = video_addr
        if enable_rtsp_over_tcp:
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        self.vid = cv2.VideoCapture(self.video_addr)
        if not self.vid.isOpened():
            raise IOError("Couldn't open webcam or video")
        self.video_fps = int(self.vid.get(cv2.CAP_PROP_FPS))
        self.video_size = (int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)),
                           int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    def width(self):
        return self.video_size[0]

    def height(self):
        return self.video_size[1]

    def fps(self):
        return self.video_fps

    def read(self):
        return self.vid.read()

    def close(self):
        if self.vid is not None:
            self.vid.release()

    def __eq__(self, other):
        return self.video_addr == other.video_addr

    def copy(self):
        return VideoReader(video_addr=self.video_addr)

class BufferedVideoReader(VideoSource, ABC):
    """对视频流进行缓存"""

    def __init__(self, video_source: VideoSource, buffer_size=30):
        self.video_source = video_source
        self.buffer_size = buffer_size
        self.image_buffer = queue.Queue(buffer_size)
        self.is_finished = False

        parent = self

        def reader():
            while not parent.is_finished:
                for i in range(buffer_size):
                    return_value, frame = parent.video_source.read()
                    if not return_value:
                        parent.is_finished = True
                        break

                    # print(parent.image_buffer.qsize())
                    parent.image_buffer.put(frame)

        read_thread = threading.Thread(target=reader)
        read_thread.daemon = True
        read_thread.start()

    def read(self):
        while not self.is_finished:
            if not self.image_buffer.empty():
                return True, self.image_buffer.get()
        return False, None

    def close(self):
        self.is_finished = True
        self.video_source.close()

    def __eq__(self, other):
        return self.video_source == other.video_source

    def copy(self):
        return BufferedVideoReader(video_source=self.video_source, buffer_size=self.buffer_size)

    def fps(self):
        return self.video_source.fps()

    def width(self):
        return self.video_source.width()

    def height(self):
        return self.video_source.height()