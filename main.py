import web_ui
import camera
import printer
import asyncio
import queue

log_queue = queue.Queue()

async def main():
    # await printer.initialize()
    web_ui.start_app()


if __name__ == "__main__":
    asyncio.run(main())    
