import common
import camera
import printer

from flask import Flask, Response, stream_with_context, jsonify
import json
import asyncio
import time


app = Flask(__name__)
html_code = "\n".join(open("ui.html").readlines())

@app.route('/logs')
def get_logs():
    return jsonify(common.logs)

@app.route('/printer_stats')
def stream_printer_stats():
    def event_stream():
        while True:
            if common.printer_stats == None:
                common.printer_stats = f"data: {json.dumps({'state': 'UNKNOWN'})}\n\n"
            yield common.printer_stats
            time.sleep(0.2)
            
    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

@app.route('/stream_logs')
def stream_logs():
    def event_stream():
        last_index = len(common.logs)
        while True:
            if len(common.logs) > last_index:
                for i in range(last_index, len(common.logs)):
                    yield f"data: {json.dumps({'log': common.logs[i]})}\n\n"
                last_index = len(common.logs)
            time.sleep(0.2)
            
    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

@app.route('/video_feed')
def video_feed():
    if not common.camera_found:
        return Response("CAMERA_NOT_FOUND", status=404, mimetype='text/plain')
    
    common.log_event("Camera feed started")
    return Response(camera.generate_frames(100),
                    mimetype='multipart/x-mixed-replace; boundary=endofframe')

@app.route('/')
def index():
    return html_code

def start_app():
    common.log_event("Socket bound to port 5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)