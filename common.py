import queue
import time

camera_found = False
log_queue = queue.Queue()

def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    log_queue.put(f"[{timestamp}] {message}")