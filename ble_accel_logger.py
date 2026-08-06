"""
Nano 33 IoTからBLE経由で加速度データ(X,Y,Z)を受信し,CSVに保存するスクリプト.

事前準備:
    pip install bleak

使い方:
    python ble_accel_logger.py
"""
from dotenv import load_dotenv
import os
import asyncio
import struct
import csv
from datetime import datetime
from pathlib import Path
from bleak import BleakScanner, BleakClient

load_dotenv()

# Arduino側のスケッチで定義したUUIDと合わせる
SERVICE_UUID = os.getenv('SERVICE_UUID')
CHARACTERISTIC_UUID = os.getenv('CHARACTERISTIC_UUID')

# Arduino側でBLE.setLocalName()に設定した名前
DEVICE_NAME = os.getenv('DEVICE_NAME')

# 保存先ディレクトリ
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# 保存先CSVファイル名(実行のたびにタイムスタンプ付きで新規作成)
CSV_FILENAME = DATA_DIR / f"accel_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"


def notification_handler(csv_writer):
    """
    BLEのnotifyを受け取るたびに呼ばれるコールバック関数を返す.
    12バイト(float×3, リトルエンディアン)をX,Y,Zに変換してCSVに書き込む.
    """
    def handler(sender, data: bytearray):
        if len(data) != 12:
            print(f"想定外のデータ長です: {len(data)} bytes")
            return

        x, y, z = struct.unpack("<fff", data)
        timestamp = datetime.now().isoformat(timespec="milliseconds")

        print(f"{timestamp}  X={x:+.3f}  Y={y:+.3f}  Z={z:+.3f}")
        csv_writer.writerow([timestamp, x, y, z])

    return handler


async def main():
    print("Nano 33 IoT (AccelSensor) をスキャン中...")

    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name == DEVICE_NAME
    )

    if device is None:
        print(f"デバイス '{DEVICE_NAME}' が見つかりませんでした.")
        print("Arduino側の電源が入っているか,アドバタイズ中か確認してください.")
        return

    print(f"デバイスが見つかりました: {device.name} ({device.address})")

    with open(CSV_FILENAME, mode="w", newline="", encoding="utf-8") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["timestamp", "x", "y", "z"])  # ヘッダー行

        async with BleakClient(device) as client:
            print(f"接続しました. Ctrl+C で終了します. 保存先: {CSV_FILENAME}")

            await client.start_notify(
                CHARACTERISTIC_UUID, notification_handler(csv_writer)
            )

            try:
                # 接続を維持し続ける(Ctrl+Cで終了するまで待機)
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\n終了処理中...")
            finally:
                await client.stop_notify(CHARACTERISTIC_UUID)

    print(f"CSVファイルに保存しました: {CSV_FILENAME}")


if __name__ == "__main__":
    asyncio.run(main())