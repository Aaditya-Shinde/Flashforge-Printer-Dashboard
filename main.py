import common
import web_ui
import camera
import printer

import json
import threading
import asyncio

async def main():
    flask_thread = threading.Thread(target=web_ui.start_app, daemon=True)
    flask_thread.start()

    camera.initialize()

    await printer.initialize()

    common.keep_open()

if __name__ == "__main__":
    asyncio.run(main())    
