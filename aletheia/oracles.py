from typing import Any, Dict, Tuple, List
from collections import Counter
from .core import register_oracle
import math

def is_sorted(a: List[int]) -> bool:
    return all(a[i] <= a[i+1] for i in range(len(a)-1))

def is_permutation(a: List[int], b: List[int]) -> bool:
    return Counter(a) == Counter(b)

@register_oracle("sort_correctness")
def sort_correctness_oracle(inp: Any, out: Any) -> Tuple[bool, Dict[str, Any]]:
    ok = isinstance(out, list) and is_sorted(out) and is_permutation(inp, out)
    details = {}
    if not ok: details["reason"] = "not_sorted_or_not_permutation"
    return ok, details

@register_oracle("dot_correctness")
def dot_correctness_oracle(inp: Any, out: Any):
    x = inp["x"]; y = inp["y"]
    baseline = math.fsum([xi*yi for xi, yi in zip(x,y)])
    ok = math.isfinite(out) and abs(out - baseline) <= 1e-6 * (1.0 + abs(baseline))
    return ok, ({} if ok else {"baseline": baseline, "observed": out})