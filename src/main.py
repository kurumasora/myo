"""
AccelPointer エントリポイント.

使い方:
    python src/main.py
"""

import asyncio
import queue
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import ble_receiver, display

_QUEUE_MAXSIZE = 5


def main() -> None:
    data_queue: queue.Queue = queue.Queue(maxsize=_QUEUE_MAXSIZE)

    def ble_thread() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        stop_event = asyncio.Event()
        try:
            loop.run_until_complete(ble_receiver.run(data_queue, stop_event))
        except Exception as e:
            print(f"BLEエラー: {e}")
        finally:
            loop.close()

    threading.Thread(target=ble_thread, daemon=True).start()

    try:
        display.run(data_queue)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
