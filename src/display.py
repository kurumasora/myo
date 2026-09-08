"""加速度の二重積分によるポインタ表示. R キーでリセット."""

import queue
import sys

import pygame

from src.pointer import PointerController

_BG      = (20, 20, 30)
_POINTER = (80, 160, 255)
_TEXT    = (120, 120, 140)
_GREEN   = (60, 200, 100)
_YELLOW  = (200, 160, 60)

_SENSITIVITY = 5000.0  # [g·s²] → [px]


def run(data_queue: "queue.Queue") -> None:
    pointer = PointerController(sample_rate=30.0)

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("AccelPointer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    w, h = screen.get_size()
    cx, cy = w / 2.0, h / 2.0
    connected = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_r:
                    pointer.reset()

        latest = None
        while True:
            try:
                latest = data_queue.get_nowait()
            except queue.Empty:
                break

        if latest is not None:
            connected = True
            ax, ay, az, gx, gy, gz = latest
            pointer.update(ax, ay, az, gx, gy, gz)

        px, py = pointer.position
        draw_x = max(0, min(w, int(cx + px * _SENSITIVITY)))
        draw_y = max(0, min(h, int(cy + py * _SENSITIVITY)))

        screen.fill(_BG)
        pygame.draw.circle(screen, _POINTER, (draw_x, draw_y), 20)
        pygame.draw.circle(screen, _GREEN if connected else _YELLOW, (16, 16), 7)
        screen.blit(font.render(
            "BLE: Connected" if connected else "BLE: Waiting...", True, _TEXT), (28, 8))

        if connected:
            screen.blit(font.render(
                f"px:{px:+.4f}  py:{py:+.4f}   [R] reset", True, _TEXT), (10, h - 26))

        pygame.display.flip()
        clock.tick(60)
