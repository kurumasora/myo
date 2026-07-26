"""
AccelPointer - BLE加速度センサによる画面ポインタ制御

使い方:
    cd src
    python main.py

依存:
    pip install bleak pygame
"""

import asyncio
import queue
import threading

import ble_receiver
import display

_QUEUE_MAXSIZE = 5


def main() -> None:
    data_queue: queue.Queue[tuple[float, float, float]] = queue.Queue(
        maxsize=_QUEUE_MAXSIZE
    )

    # asyncio.Eventはイベントループに紐づくため、BLEスレッド側で作成する
    stop_event_holder: list[asyncio.Event] = []

    def ble_thread_target() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        stop_event = asyncio.Event()
        stop_event_holder.append(stop_event)
        try:
            loop.run_until_complete(ble_receiver.run(data_queue, stop_event))
        except Exception as e:
            print(f"BLEスレッドでエラー: {e}")
        finally:
            loop.close()

    ble_thread = threading.Thread(target=ble_thread_target, daemon=True)
    ble_thread.start()

    try:
        # pygame はメインスレッドで動かす（macOS制約）
        display.run(data_queue)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
