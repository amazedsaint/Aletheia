from typing import Any, List
from .core import register_impl
import random

@register_impl("buggy_quicksort")
def buggy_quicksort(a: List[int], rng: random.Random) -> List[int]:
    if len(a) <= 1: return a[:]
    pivot = a[len(a)//2]
    left  = [x for x in a if x < pivot]
    right = [x for x in a if x > pivot]
    return buggy_quicksort(left, rng) + [pivot] + buggy_quicksort(right, rng)

@register_impl("quicksort3")
def quicksort_3way(a: List[int], rng: random.Random) -> List[int]:
    if len(a) <= 1: return a[:]
    pivot = a[len(a)//2]
    lt = [x for x in a if x < pivot]
    eq = [x for x in a if x == pivot]
    gt = [x for x in a if x > pivot]
    return quicksort_3way(lt, rng) + eq + quicksort_3way(gt, rng)

@register_impl("dot_naive")
def dot_naive(inp: dict, rng: random.Random) -> float:
    x = inp["x"]; y = inp["y"]
    s = 0.0
    for xi, yi in zip(x, y): s += xi*yi
    return s

@register_impl("dot_kahan")
def dot_kahan(inp: dict, rng: random.Random) -> float:
    x = inp["x"]; y = inp["y"]
    s = 0.0; c = 0.0
    for xi, yi in zip(x,y):
        prod = xi*yi
        yk = prod - c
        t = s + yk
        c = (t - s) - yk
        s = t
    return s