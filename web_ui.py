import camera
import json
from flask import Flask, Response, stream_with_context


app = Flask(__name__)
html_code = "\n".join(open("ui.html").readlines())

def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    log_queue.put(f"[{timestamp}] {message}")

@app.route('/stream_logs')
def stream_logs():
    def event_stream():
        while True:
            # Wait for new log messages from the queue
            msg = log_queue.get()
            yield f"data: {json.dumps({'log': msg})}\n\n"
    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

@app.route('/video_feed')
def video_feed():
    return Response(camera.generate_frames(70),
                    mimetype='multipart/x-mixed-replace; boundary=endofframe')

@app.route('/')
def index():
    return html_code

def start_app():
    app.run(host='0.0.0.0', port=5000, threaded=True)