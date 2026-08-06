# myo2

Arduino Nano 33 IoT の加速度センサをBLE経由でPCに送信し，腕の動きで画面上のポインタをリアルタイム操作するシステム．

## 必要なもの

**ハードウェア**
- Arduino Nano 33 IoT（加速度センサ LSM6DS3 内蔵）

**ソフトウェア**
- Python 3.11 以上
- BLEが使用可能なPC（macOS推奨）

## セットアップ

```bash
git clone <リポジトリURL>
cd myo2
```

```bash
python -m venv myotaro
source myotaro/bin/activate  # Windows: myotaro\Scripts\activate
```

```bash
pip install bleak pygame
```

## Arduinoのセットアップ

Arduino IDEで以下のライブラリをインストールする：

- `ArduinoBLE`
- `Arduino_LSM6DS3`

スケッチを書き込み，シリアルモニタで加速度データが出力されていることを確認してから接続する．

> BLE のデバイス名が `Arduino`，UUIDが `19b10001-e8f2-537e-4f6c-d104768a1214` であることを前提としている．異なる場合は `src/ble_receiver.py` の定数を変更すること．

## 使い方

### ポインタ操作（メイン機能）

Arduinoの電源を入れてアドバタイズ状態にしてから実行する．

```bash
cd src
python main.py
```

- デバイスが見つかると pygame ウィンドウが開き，腕の傾きに応じてポインタが動く
- `Esc` またはウィンドウを閉じると終了

### 加速度ログの記録

```bash
python ble_accel_logger.py
```

`data/accel_log_YYYYMMDD_HHMMSS.csv` に保存される．`Ctrl+C` で終了．

### BLEデバイスの確認

デバイスが見つからない場合のデバッグ用．

```bash
python ble_scan_debug.py
```

## プロジェクト構成

```
myo2/
├── src/
│   ├── main.py          # エントリーポイント
│   ├── ble_receiver.py  # BLE受信（asyncio）
│   ├── filter.py        # 適応フィルタ（キャリブレーション不要）
│   └── display.py       # pygame リアルタイム描画
├── ble_accel_logger.py  # 加速度をCSVに記録するユーティリティ
├── ble_scan_debug.py    # BLEスキャンデバッグ用
└── data/                # ログCSV保存先（.gitignore対象）
```

## アルゴリズム概要

キャリブレーションなしで誰でも使えるよう，2段階の適応フィルタを採用している．

```
生の加速度 [g]
  ↓ 高速EMA（α=0.2）         ノイズ除去
  ↓ 低速EMA（α=0.002）       安静時のゼロ点を自動推定
  ↓ 最大偏差で正規化          個人の可動域に自動適応
  → [-1.0, 1.0]
  ↓ 画面サイズにマッピング
  ↓ Lerp補間（α=0.15）       視覚的ななめらかさ
  → 画面座標 (px)
```

- **ゼロ点の自動推定**：人によって異なる「自然な持ち方」の傾きを，安静時の長期平均として動的に学習する
- **可動域の自動推定**：観測された最大偏差を追跡し，使うほどその人の動きの幅に適応する

## トラブルシューティング

**デバイスが見つからない**
- macOS のシステム設定 > プライバシーとセキュリティ > Bluetooth でターミナル／Python に権限を付与する
- `python ble_scan_debug.py` でデバイスが見えているか確認する

**ポインタがふらつく**
- 起動直後はゼロ点が収束していないため数秒間ふらつくのは正常
- 安静にした状態で10秒ほど待つと安定する
