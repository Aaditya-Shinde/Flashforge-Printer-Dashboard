import io
import time
from PIL import Image
from picamera2 import Picamera2

picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480), "format": "BGR888"})
picam2.configure(config)
picam2.start()

def generate_frames(stream_quality):
    while True:
        frame_bytes = capture_frame(frame_quality=stream_quality)

        yield (b'--endofframe\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.02)

def capture_frame(frame_quality):
    frame_array = picam2.capture_array("main")
    img = Image.fromarray(frame_array)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=frame_quality)
    frame_bytes = buffer.getvalue()
    return frame_bytes