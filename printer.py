import common
import asyncio
import os
import json
from flashforge import FlashForgeClient, FiveMClientConnectionOptions, PrinterDiscovery
from flashforge.models.machine_info import Temperature
from dotenv import load_dotenv

load_dotenv()
printer_client = None
attributes_to_query = ["machine_state", "cooling_fan_speed", "print_bed", "extruder"]

async def initialize():
    global printer_client

    common.printer_stats = f"data: {json.dumps({'MACHINE_STATE': 'CONNECTING'})}\n\n"

    check_code = os.getenv("CHECK_CODE", "").strip()
    expected_serial = os.getenv("EXPECTED_SERIAL_NUMBER", "").strip()

    common.log_event("Scanning network...")
    discovery = PrinterDiscovery()
    printers = await discovery.discover()

    if not printers:
        common.log_event("No printer clients found")
        return

    target_printer = printers[0]
    if expected_serial:
        for p in printers:
            if p.serial_number == expected_serial:
                target_printer = p
                break

    common.log_event(f"Printer found at {target_printer.ip_address}")
    
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
        common.log_event(f"Connection established to {client.printer_name}")

        await client.init_control()
        common.log_event("Control session initialized")
        printer_client = client

async def start_status_poller():
    global printer_client

    while True:
        try:
            status = await printer_client.get_printer_status()
            
            if status is None:
                common.printer_stats = f"data: {json.dumps({'MACHINE_STATE': 'DISCONNECTED'})}\n\n"
            else:
                data_dictionary = {}
                for attribute in attributes_to_query:
                    attribute_val = getattr(status, attribute)
                    
                    if isinstance(attribute_val, Temperature):
                        attribute_val_str = f"{round(attribute_val.current, 1)}/{round(attribute_val.set, 1)} °C"
                    else:
                        attribute_val_str = attribute_val.name if hasattr(attribute_val, 'name') else str(attribute_val)

                    data_dictionary[attribute.upper()] = attribute_val_str

                common.printer_stats = f"data: {json.dumps(data_dictionary)}\n\n"
                
        except Exception as e:
            common.log_event("ERROR: "+e)
        
        await asyncio.sleep(2)

async def print_file_path(file_path):
    if not os.path.exists(file_path):
        common.log_event(f"File not Found: {file_path}")
        return

    await printer_client.control.home_axes()
    common.log_event("Axes homed successfully.")

    common.log_event(f"Uploading {file_path}...")
    await printer_client.job_control.upload_file_path(file_path, start_print=True, level_before_print=False)
    common.log_event("file_path upload complete.")