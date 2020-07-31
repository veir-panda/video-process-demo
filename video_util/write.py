import logging
import subprocess
from abc import ABCMeta, abstractmethod, ABC
import cv2


class VideoWriterClass(metaclass=ABCMeta):
    @abstractmethod
    def write(self, frame):
        pass

    @abstractmethod
    def close(self):
        pass


class LocalVideoWriter(VideoWriterClass, ABC):
    def __init__(self, target_path, fps, size):
        self.vid = cv2.VideoWriter(target_path, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, size)
        # self.vid = cv2.VideoWriter(target_path, cv2.VideoWriter_fourcc('F', 'L', 'V', '1'), fps, size)
        if not self.vid.isOpened():
            raise IOError("Couldn't write video stream")

    def write(self, frame):
        """
        :param frame: BGR格式的帧图像
        :return:
        """
        self.vid.write(frame)

    def close(self):
        if self.vid is not None:
            self.vid.release()

class VideoWriterWithFFMpeg(VideoWriterClass, ABC):
    __ffmpeg_path = '/usr/bin/ffmpeg'

    @staticmethod
    def init(ffmpeg_path):
        VideoWriterWithFFMpeg.__ffmpeg_path = ffmpeg_path

    def __init__(self, target_path, fps, size):
        self.rtmp_url = target_path

        # 管道输出 ffmpeg推送rtmp
        command = [VideoWriterWithFFMpeg.__ffmpeg_path,
                   # '-y',
                   # '-loglevel', 'error',
                   # '-loglevel', 'panic',
                   '-f', 'rawvideo',
                   # '-hwaccel','cuvid',
                   # '-c:v', 'libx264',
                   '-vcodec', 'rawvideo',
                   '-pix_fmt', 'bgr24',
                   # '-pix_fmt', 'yuv420p',
                   '-s', f'{size[0]}*{size[1]}',
                   '-r', str(fps),
                   '-i', '-',
                   '-c:v', 'libx264',
                   # '-c:v', 'h264_nvenc',
                   '-pix_fmt', 'yuv420p',
                   # '-s', '1920*1080',
                   # '-preset', 'ultrafast',
                   '-f', 'flv',
                   self.rtmp_url,
                   ]

        self.pipe = subprocess.Popen(command, stdin=subprocess.PIPE)  # ,shell=False
        print(" ".join(command))
        logging.info(f'pushing rtmp to {self.rtmp_url}')
        self._is_inited = True

    def write(self, frame):
        """
        :param frame: cv2中BGR格式的帧图像
        :return:
        """
        if not self._is_inited:
            raise RuntimeError("rtmp push util is not inited or has been stop.")
        try:
            self.pipe.stdin.write(frame.tostring())
        except BaseException as e:
            logging.error(str(e))
            self.close()
            raise e

    def close(self):
        if self.pipe:
            self.pipe.stdin.close()
            if self.pipe.stderr is not None:
                self.pipe.stderr.close()
            self.pipe.wait()
            self.pipe.terminate()
            self.pipe = None
        self._is_inited = False
