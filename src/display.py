"""
適応フィルタを通した加速度値をもとに、画面上のポインタをリアルタイム描画する.
6軸データのうち加速度(ax, ay)のみをポインタ位置に使用する.
"""

import queue
import sys

import pygame

from filter import AdaptiveFilter

_BG_COLOR = (20, 20, 30)
_POINTER_COLOR = (80, 160, 255)
_TEXT_COLOR = (120, 120, 140)
_CONNECTED_COLOR = (60, 200, 100)
_WAITING_COLOR = (200, 160, 60)

_LERP_ALPHA = 0.15


def run(data_queue: "queue.Queue[tuple[float, float, float, float, float, float]]") -> None:
    filters = {
        "x": AdaptiveFilter(),
        "y": AdaptiveFilter(),
    }

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("AccelPointer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    w, h = screen.get_size()
    pos_x, pos_y = w / 2.0, h / 2.0
    connected = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        latest = None
        while True:
            try:
                latest = data_queue.get_nowait()
            except queue.Empty:
                break

        if latest is not None:
            connected = True
            ax, ay, az, gx, gy, gz = latest
            norm_x = filters["x"].update(ax)
            norm_y = filters["y"].update(ay)

            target_x = w / 2 + norm_x * (w / 2 - 20)
            target_y = h / 2 + norm_y * (h / 2 - 20)

            pos_x += _LERP_ALPHA * (target_x - pos_x)
            pos_y += _LERP_ALPHA * (target_y - pos_y)

        screen.fill(_BG_COLOR)
        pygame.draw.circle(screen, _POINTER_COLOR, (int(pos_x), int(pos_y)), 20)

        status_color = _CONNECTED_COLOR if connected else _WAITING_COLOR
        status_text = "BLE: Connected" if connected else "BLE: Waiting..."
        pygame.draw.circle(screen, status_color, (16, 16), 7)
        label = font.render(status_text, True, _TEXT_COLOR)
        screen.blit(label, (28, 8))

        if connected:
            debug = (
                f"baseline  X:{filters['x'].baseline:+.3f}  "
                f"Y:{filters['y'].baseline:+.3f}   "
                f"range  X:{filters['x'].max_deviation:.3f}  "
                f"Y:{filters['y'].max_deviation:.3f}"
            )
            screen.blit(font.render(debug, True, _TEXT_COLOR), (10, h - 26))

        pygame.display.flip()
        clock.tick(60)
