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
    expected_serial = os.getenv("EXPECTED_SERIAL_NUMBER", "").strip()

    print("Scanning for FlashForge printers...")
    discovery = PrinterDiscovery()
    printers = await discovery.discover()

    if not printers:
        print("No printers found via network discovery.")
        return

    target_printer = printers[0]
    if expected_serial:
        for p in printers:
            if p.serial_number == expected_serial:
                target_printer = p
                break

    print(f"Connecting to printer at {target_printer.ip_address} (Serial: {target_printer.serial_number})...")
    
    options = FiveMClientConnectionOptions(
        http_port=target_printer.event_port,
        tcp_port=target_printer.command_port,
    )

    async with FlashForgeClient(
        target_printer.ip_address,
        target_printer.serial_number,
        check_code,
        options=options,
    ) as client:
        print("Connection established. Initializing control session...")
        await client.init_control()
        printer_client = client

    await start_status_poller()

async def start_status_poller():
    global printer_client

    print("In status poller")

    while True:
        try:
            status = await printer_client.get_printer_status()
            if status:
                common.printer_status = status
                print(f"[POLL SUCCESS] Machine State: {status.machine_state}")
        except:
            continue
        
        await asyncio.sleep(2)

async def get_stats():
    status = common.printer_status

    state = status.machine_state
    state_str = state.name if hasattr(state, 'name') else str(state)
    return f"data: {json.dumps({'state': state_str})}\n\n"

async def print_file_path(file_path):
    if not os.path.exists(file_path):
        common.log_event(f"File not Found: {file_path}")
        return

    await printer_client.control.home_axes()
    common.log_event("Axes homed successfully.")

    common.log_event(f"Uploading {file_path}...")
    await printer_client.job_control.upload_file_path(file_path, start_print=True, level_before_print=False)
    common.log_event("file_path upload complete.")