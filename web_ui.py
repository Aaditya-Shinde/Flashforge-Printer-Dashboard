import camera
from flask import Flask, Response

app = Flask(__name__)
html_code = "\n".join(open("ui.html").readlines())

@app.route('/video_feed')
def video_feed():
    return Response(camera.generate_frames(70),
                    mimetype='multipart/x-mixed-replace; boundary=endofframe')

@app.route('/')
def index():
    return html_code

def start_app():
    app.run(host='0.0.0.0', port=5000, threaded=True)