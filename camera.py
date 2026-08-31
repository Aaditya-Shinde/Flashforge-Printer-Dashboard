import common
import io
import time
from PIL import Image
from picamera2 import Picamera2

picam2 = None

def initialize():
    global picam2
    
    try:
        common.log_event("Scanning for Camera...")
        picam2 = Picamera2()
        common.log_event("Camera Found")
        config = picam2.create_video_configuration(main={"size": (640, 480), "format": "BGR888"})
        picam2.configure(config)
        common.log_event("Camera Configured")
        picam2.start()

        common.log_event("Camera Initialized")
        return True
    except RuntimeError as e:
        if 'No camera number 0 found' in str(e):
            common.log_event("Camera Not Found")
        else:
            common.log_event(f"Unkown Camera Error: {e}...")
        return False

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