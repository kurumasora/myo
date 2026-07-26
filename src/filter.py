"""
キャリブレーションなしで個人差を吸収する適応フィルタ.

- 高速EMA         : ノイズ除去
- 低速EMA baseline: 安静時の傾き（ゼロ点）を自動推定
- 最大偏差追跡    : 個人の可動域を自動推定
"""


class AdaptiveFilter:
    def __init__(
        self,
        alpha: float = 0.2,
        alpha_baseline: float = 0.002,
        decay: float = 0.9995,
        min_range: float = 0.1,
    ):
        self._alpha = alpha
        self._alpha_baseline = alpha_baseline
        self._decay = decay
        self._min_range = min_range

        self._ema = None
        self._baseline = None
        self._max_deviation = 0.2  # 初期推定可動域 [g]

    def update(self, raw: float) -> float:
        """
        生の加速度値を受け取り、[-1.0, 1.0] に正規化した値を返す.
        呼ぶたびに内部状態が更新される.
        """
        if self._ema is None:
            self._ema = raw
            self._baseline = raw
            return 0.0

        # 高速EMA（ノイズ除去）
        self._ema = self._alpha * raw + (1 - self._alpha) * self._ema

        # 低速EMA（安静時ゼロ点の自動推定）
        self._baseline = (
            self._alpha_baseline * self._ema
            + (1 - self._alpha_baseline) * self._baseline
        )

        deviation = self._ema - self._baseline

        # 最大偏差：新しい極値があれば更新、なければ徐々に縮小
        self._max_deviation = max(
            self._max_deviation * self._decay,
            abs(deviation),
            self._min_range,
        )

        return max(-1.0, min(1.0, deviation / self._max_deviation))

    @property
    def baseline(self) -> float | None:
        return self._baseline

    @property
    def max_deviation(self) -> float:
        return self._max_deviation
