import common
import asyncio
import os
import json
from flashforge import FlashForgeClient, FiveMClientConnectionOptions, PrinterDiscovery
from dotenv import load_dotenv

load_dotenv()
printer_client = None

async def initialize():
    global printer_client

    check_code = os.getenv("CHECK_CODE", "").strip()
    if not check_code:
        common.log_event('CHECK_CODE not set')

    discovery = PrinterDiscovery()

    common.log_event("Scanning for printer clients...")
    printer_clients = await discovery.discover()
        
    if not printer_clients:
        common.log_event("No printer clients found")
        return

    common.log_event("Printer client found")
    printer_client = printer_clients[0]
    if not printer_client.serial_number:
        common.log_event("No serial number reported")
        return

    options = FiveMClientConnectionOptions(
        http_port=printer_client.event_port,
        tcp_port=printer_client.command_port,
    )

    printer_client = FlashForgeClient(
        printer_client.ip_address,
        printer_client.serial_number,
        check_code,
        options=options,
    )
    common.log_event("Printer client authentication successful")
    common.printer_found = True

    await printer_client.init_control()
    common.log_event("Printer client initialized")

    asyncio.create_task(start_status_poller())

async def start_status_poller():
    global printer_client
    while True:
        await asyncio.sleep(1)
        if printer_client is None:
            continue

        try:
            status = await printer_client.get_printer_status()
            if status:
                common.printer_status = status
        except:
            continue

async def get_stats():
    status = common.printer_status
    
    return f"data: {json.dumps({'state': status.machine_state})}\n\n"

async def print_file_path(file_path):
    if not os.path.exists(file_path):
        common.log_event(f"File not Found: {file_path}")

    await printer_client.control.home_axes()
    common.log_event("Axes homed successfully.")

    common.log_event(f"Uploading {file_path}...")
    await printer_client.job_control.upload_file_path(file_path, start_print=True, level_before_print=False)
    common.log_event("file_path upload complete.")
