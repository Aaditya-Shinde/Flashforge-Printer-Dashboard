import asyncio
import os
from flashforge import FlashForgeClient, FiveMClientConnectionOptions, PrinterDiscovery
from dotenv import load_dotenv

load_dotenv()
printer_client = None

async def print_file_path(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"G-code file_path not found at: {file_path}")

    await printer_client.control.home_axes()
    print("Axes homed successfully.")

    # Upload the G-code file_path to the printer_client storage
    print(f"Uploading {file_path}...")
    await printer_client.job_control.upload_file_path(file_path, start_print=True, level_before_print=False)
    print("file_path upload complete.")

async def initialize():
    global printer_client

    check_code = os.getenv("CHECK_CODE", "").strip()
    if not check_code:
        raise ValueError('CHECK_CODE not set')

    discovery = PrinterDiscovery()
    printer_clients = await discovery.discover()

    if not printer_clients:
        raise ConnectionError("No printer clients found")

    printer_client = printer_clients[0]
    if not printer_client.serial_number:
        raise PermissionError("Discovered printer_client did not report a serial number")

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

    await printer_client.init_control()

async def get_status():
    status = await printer_client.get_printer_client_status()
    if not status:
        raise ValueError("Invalid State")
    return status #status has temps, state, eta, ...