import common
import asyncio
import os
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
    try:
        async with asyncio.timeout(1) as cm:
            common.log_event("Scanning for printer clients...")
            printer_clients = await discovery.discover()
    except asyncio.TimeoutError:
        common.log_event("No printer clients found")
        return
        
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

    await printer_client.init_control()
    common.log_event("Printer client initialized")

async def print_file_path(file_path):
    if not os.path.exists(file_path):
        common.log_event(f"File not Found: {file_path}")

    await printer_client.control.home_axes()
    common.log_event("Axes homed successfully.")

    common.log_event(f"Uploading {file_path}...")
    await printer_client.job_control.upload_file_path(file_path, start_print=True, level_before_print=False)
    common.log_event("file_path upload complete.")

async def get_status():
    status = await printer_client.get_printer_client_status()
    if not status:
        raise ValueError("Invalid State")
    return status #status has temps, state, eta, ...