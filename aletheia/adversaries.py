from typing import Any, Dict
import random
from .core import register_generator

@register_generator("dup_heavy_small")
def duplicates_biased(rng: random.Random, params: Dict[str, Any]) -> list:
    nmin = params.get("nmin", 0); nmax = params.get("nmax", 12)
    vmin, vmax = params.get("range", (0,9))
    n = rng.randint(nmin, nmax)
    return [rng.randint(vmin, vmax) for _ in range(n)]

@register_generator("nearly_sorted")
def nearly_sorted(rng: random.Random, params: Dict[str, Any]) -> list:
    n = rng.randint(params.get("nmin", 64), params.get("nmax", 512))
    vmin, vmax = params.get("range", (0, 10_000_000))
    swaps_frac = rng.uniform(params.get("swaps_min", 0.005), params.get("swaps_max", 0.08))
    swaps = max(1, int(swaps_frac * n))
    a = sorted(rng.randint(vmin, vmax) for _ in range(n))
    for _ in range(swaps):
        i, j = rng.randrange(n), rng.randrange(n)
        a[i], a[j] = a[j], a[i]
    return a

@register_generator("float_dot_vectors")
def float_dot_vectors(rng: random.Random, params: Dict[str, Any]) -> dict:
    n = rng.randint(params.get("nmin", 64), params.get("nmax", 2048))
    hi = params.get("hi", 1e16); lo = params.get("lo", 1e-16)
    x = [(rng.random() - 0.5) * (hi if rng.random()<0.5 else lo) for _ in range(n)]
    y = [(rng.random() - 0.5) * (hi if rng.random()<0.5 else lo) for _ in range(n)]
    return {"x": x, "y": y}