import queue
import time

camera_found = False
printer_found = False
printer_status = None
logs = []

def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    logs.append(f"[{timestamp}] {message}")