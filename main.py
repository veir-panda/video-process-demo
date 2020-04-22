import logging

from video_util.read import VideoReader, BufferedVideoReader
from video_util.write import LocalVideoWriter, VideoWriterWithFFMpeg

import cv2
import numpy as np

if __name__ == '__main__':
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    source = "rtsp://player.daniulive.com:554/live27640.sdp"
    rtmp = "rtmp://172.18.0.152:1935/live/demo"
    # rtmp = "1.mp4"

    reader = VideoReader(source)
    reader = BufferedVideoReader(reader)

    fps = reader.fps()
    size = reader.width(), reader.height()

    ffmpeg_path = "D:/download/ffmpeg-20190826-0821bc4-win64-static/bin/ffmpeg"
    VideoWriterWithFFMpeg.init(ffmpeg_path)     #设置ffmpeg的命令路径
    writer = VideoWriterWithFFMpeg(rtmp, fps, size)

    while True:
        ret, frame = reader.read()
        if ret:
            print(f"read frame size={str(size)}")

            #处理帧，帧为BGR通道的图像
            #...........
            #处理帧，帧为BGR通道的图像

            # 转为numpy数组
            frame = np.fromstring(frame, dtype='uint8')
            # 写入rtmp视频流(BGR通道)
            writer.write(frame)

            # show a frame
            # cv2.imshow("capture", frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

    reader.close()
    writer.close()

    # cv2.destroyAllWindows()

