"""ay, az を二重積分して画面座標を返す."""


class PointerController:
    def __init__(self, sample_rate: float = 30.0):
        self._dt = 1.0 / sample_rate
        self._vx = 0.0
        self._vy = 0.0
        self._px = 0.0
        self._py = 0.0

    def update(self, ax: float, ay: float, az: float,
               gx: float, gy: float, gz: float) -> tuple[float, float]:
        self._vx += ay * self._dt          # Y軸 → 画面X
        self._vy += (az - 1.0) * self._dt
        self._px += self._vx * self._dt
        self._py += self._vy * self._dt
        return self._px, self._py

    def reset(self) -> None:
        self._vx = self._vy = self._px = self._py = 0.0

    @property
    def position(self) -> tuple[float, float]:
        return self._px, self._py
