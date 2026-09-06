import common
import web_ui
import camera
import printer

import asyncio

async def main():
    await printer.initialize()
    # common.camera_found = camera.initialize()
    # web_ui.start_app()


if __name__ == "__main__":
    asyncio.run(main())    
