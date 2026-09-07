import queue
import time

camera_found = False

printer_stats = None

logs = []

def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    logs.append(f"[{timestamp}] {message}")