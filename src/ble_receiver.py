"""
BLE経由でArduino Nano 33 IoTから6軸IMUデータを受信し、キューに流す.
送信フォーマット: float × 6 = 24バイト (ax, ay, az, gx, gy, gz)
"""

import asyncio
import struct
import queue

from bleak import BleakScanner, BleakClient

SERVICE_UUID = "19b10000-e8f2-537e-4f6c-d104768a1214"
CHARACTERISTIC_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214"
DEVICE_NAME = "AccelSensor"


async def run(data_queue: queue.Queue, stop_event: asyncio.Event) -> None:
    print(f"'{DEVICE_NAME}' をスキャン中...")

    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: ad.local_name == DEVICE_NAME
    )

    if device is None:
        print(f"デバイス '{DEVICE_NAME}' が見つかりませんでした.")
        stop_event.set()
        return

    print(f"接続: {device.name} ({device.address})")

    def handler(sender, data: bytearray) -> None:
        if len(data) == 24:
            ax, ay, az, gx, gy, gz = struct.unpack("<ffffff", data)
            if data_queue.full():
                try:
                    data_queue.get_nowait()
                except queue.Empty:
                    pass
            data_queue.put_nowait((ax, ay, az, gx, gy, gz))

    async with BleakClient(device) as client:
        await client.start_notify(CHARACTERISTIC_UUID, handler)
        print("受信中. Ctrl+C またはウィンドウを閉じると終了します.")
        try:
            await stop_event.wait()
        finally:
            await client.stop_notify(CHARACTERISTIC_UUID)
