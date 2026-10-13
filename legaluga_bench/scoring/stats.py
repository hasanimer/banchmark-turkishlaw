"""İstatistik yardımcıları: bootstrap güven aralığı, eşleştirilmiş fark ve McNemar testi.

Rastgelelik sabit tohumla üretilir; aynı veriyle rapor her zaman aynı çıkar.
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence


def mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def bootstrap_ci(xs: Sequence[float], n_boot: int = 2000, alpha: float = 0.05, seed: int = 7) -> tuple[float, float]:
    if not xs:
        return float("nan"), float("nan")
    rng = random.Random(seed)
    n = len(xs)
    means = sorted(sum(xs[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot))
    lo = means[int((alpha / 2) * n_boot)]
    hi = means[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    return lo, hi


def paired_bootstrap_diff(
    a: Sequence[float], b: Sequence[float], n_boot: int = 2000, alpha: float = 0.05, seed: int = 11
) -> dict[str, float]:
    """Aynı görevlerde iki sistemin puan farkı (a - b): ortalama, güven aralığı ve tek yönlü p."""
    if len(a) != len(b) or not a:
        raise ValueError("eşleştirilmiş diziler aynı uzunlukta ve boş olmamalı")
    diffs = [x - y for x, y in zip(a, b)]
    rng = random.Random(seed)
    n = len(diffs)
    boots = sorted(sum(diffs[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot))
    lo = boots[int((alpha / 2) * n_boot)]
    hi = boots[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    p_le_zero = sum(1 for v in boots if v <= 0) / n_boot
    return {"mean_diff": mean(diffs), "ci_low": lo, "ci_high": hi, "p_a_not_better": p_le_zero, "n": n}


def mcnemar_exact(a_correct: Sequence[bool], b_correct: Sequence[bool]) -> dict[str, float]:
    """İkili doğru/yanlış sonuçlar için kesin (binom) McNemar testi, çift yönlü p."""
    if len(a_correct) != len(b_correct):
        raise ValueError("diziler aynı uzunlukta olmalı")
    only_a = sum(1 for x, y in zip(a_correct, b_correct) if x and not y)
    only_b = sum(1 for x, y in zip(a_correct, b_correct) if y and not x)
    n = only_a + only_b
    if n == 0:
        return {"only_a": 0, "only_b": 0, "p_value": 1.0}
    k = min(only_a, only_b)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2**n
    return {"only_a": only_a, "only_b": only_b, "p_value": min(1.0, 2 * p)}
