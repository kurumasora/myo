"""
周辺のBLEデバイスをすべてスキャンして,名前とアドレスを表示するデバッグ用スクリプト.
AccelSensorが見つからない場合,このスクリプトでまず何が見えているか確認する.

使い方:
    python ble_scan_debug.py
"""

import asyncio
from bleak import BleakScanner


async def main():
    print("周辺のBLEデバイスを5秒間スキャンします...")
    devices = await BleakScanner.discover(timeout=5.0, return_adv=True)

    if not devices:
        print("BLEデバイスが1つも見つかりませんでした.")
        print("→ macOSのBluetooth権限(システム設定 > プライバシーとセキュリティ > Bluetooth)を確認してください.")
        return

    print(f"{len(devices)}台のデバイスが見つかりました:\n")
    for d, adv in devices.values():
        os_name = d.name if d.name else "(名前なし)"
        raw_name = adv.local_name if adv.local_name else "(広告データに名前なし)"
        print(f"  OSキャッシュ名: {os_name:20s} 広告データの名前: {raw_name:20s} アドレス: {d.address}")


if __name__ == "__main__":
    asyncio.run(main())