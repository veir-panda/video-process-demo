import logging

import torch

from video_util.video_transform import Yolo3TransformNoBuffer
from yolo3.detect.img_detect import ImageDetector

from yolo3.models.models import Darknet

from video_util.read import VideoReader, BufferedVideoReader
from video_util.write import LocalVideoWriter, VideoWriterWithFFMpeg

import cv2
import numpy as np

if __name__ == '__main__':
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    # 初始化检测模型
    # device = "cuda:0" if torch.cuda.is_available() else "cpu"
    # model = Darknet("config/yolov3.cfg")
    # model.load_darknet_weights("weights/yolov3.weights")
    # model.to(device)
    # detector = ImageDetector(model, "config/coco.names", font_path="font/sarasa-bold.ttc", font_size=28)

    # 被检测的视频流地址
    # source = "rtsp://player.daniulive.com:554/live76703.sdp"
    # source = "data/f35.flv"
    source = "D:/veir/video_20200715_155810.mp4"
    # 推流地址
    rtmp = "rtmp://172.18.0.152:1935/live/1"
    # rtmp = "1.mp4"

    enable_rtsp_over_tcp = False    # 如果使用rtsp-tcp传输视频流，则改为True
    reader = VideoReader(source, enable_rtsp_over_tcp=enable_rtsp_over_tcp)
    # reader = BufferedVideoReader(reader)
    # 目标检测 -- 图像转换
    # reader = Yolo3TransformNoBuffer(reader, detector)

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
        else:
            print("closed")
            break

    reader.close()
    writer.close()

    # cv2.destroyAllWindows()

