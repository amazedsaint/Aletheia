import json, hashlib, time, os
from dataclasses import dataclass, field, asdict
from typing import Callable, Dict, List, Optional, Tuple, Any
import concurrent.futures as cf
import random

# ---------- Deterministic seed derivation ----------
def derive_seed(master_seed: str, namespace: str, idx: int) -> int:
    m = hashlib.sha256()
    m.update(master_seed.encode()); m.update(b"|"); m.update(namespace.encode()); m.update(b"|"); m.update(str(idx).encode())
    return int.from_bytes(m.digest()[:8], "big")

# ---------- Epistemic IR ----------
@dataclass
class Domain:
    name: str
    params: Dict[str, Any]

@dataclass
class ProofArtifact:
    kind: str    # e.g., "TLA+", "SMT", "ProofSketch"
    uri: str     # path or URL
    hash: Optional[str] = None

@dataclass
class Claim:
    id: str
    proposition: str
    domain: Domain
    adversary: str                 # registered generator name
    oracle: str                    # registered oracle name
    power_alpha: float = 0.05
    trials: int = 10000
    stop_on_first_failure: bool = True
    prior: Dict[str, Any] = field(default_factory=lambda: {"type":"Beta","alpha":1,"beta":1})
    proofs: List[ProofArtifact] = field(default_factory=list)

@dataclass
class TrialResult:
    idx: int
    input_data: Any
    output_data: Any
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ClaimResult:
    claim: Claim
    failures: int
    trials_run: int
    sample_failures: List[TrialResult]
    upper95_failure_prob: Optional[float]
    rng_commit: str
    duration_sec: float

@dataclass
class BeliefCertificate:
    certVersion: str
    programHash: str
    machine: str
    createdAt: float
    claims: List[Dict[str, Any]]
    proofs: List[Dict[str, Any]] = field(default_factory=list)

def rule_of_three_upper_bound(failures: int, n: int) -> Optional[float]:
    if failures == 0 and n > 0: return 3.0 / float(n)
    return None

# ---------- Registries (plugins) ----------
GEN_REGISTRY: Dict[str, Callable[[random.Random, Dict[str, Any]], Any]] = {}
ORACLE_REGISTRY: Dict[str, Callable[[Any, Any], Tuple[bool, Dict[str, Any]]]] = {}
IMPL_REGISTRY: Dict[str, Callable[[Any, random.Random], Any]] = {}

def register_generator(name):
    def deco(fn): GEN_REGISTRY[name] = fn; return fn
    return deco

def register_oracle(name):
    def deco(fn): ORACLE_REGISTRY[name] = fn; return fn
    return deco

def register_impl(name):
    def deco(fn): IMPL_REGISTRY[name] = fn; return fn
    return deco

# ---------- Parallel falsification ----------
def parallel_trials(claim: Claim, impl_name: str, master_seed: str, max_workers: int=0) -> ClaimResult:
    gen = GEN_REGISTRY[claim.adversary]
    oracle = ORACLE_REGISTRY[claim.oracle]
    impl = IMPL_REGISTRY[impl_name]
    if max_workers <= 0:
        max_workers = min(32, (os.cpu_count() or 2))
    failures = 0
    sample_failures: List[TrialResult] = []
    t0 = time.time()
    rng_commit = hashlib.sha256((master_seed + "|" + claim.id + "|" + impl_name).encode()).hexdigest()
    stop = claim.stop_on_first_failure

    def run_one(i: int) -> TrialResult:
        seed = derive_seed(master_seed, claim.id, i)
        rng = random.Random(seed)
        inp = gen(rng, claim.domain.params)
        out = impl(inp, rng)
        ok, details = oracle(inp, out)
        return TrialResult(idx=i, input_data=inp, output_data=out, passed=ok, details=details)

    results: List[TrialResult] = []
    batch = 128
    i = 0
    with cf.ThreadPoolExecutor(max_workers=max_workers) as ex:
        while i < claim.trials:
            idxs = list(range(i, min(i+batch, claim.trials)))
            futs = [ex.submit(run_one, j) for j in idxs]
            for fut in cf.as_completed(futs):
                tr = fut.result()
                results.append(tr)
                if not tr.passed:
                    failures += 1
                    if len(sample_failures) < 5:
                        sample_failures.append(tr)
                    if stop:
                        i = claim.trials
                        break
            i += batch
            if failures and stop:
                break

    trials_run = len(results)
    upper = rule_of_three_upper_bound(failures, trials_run)
    dur = time.time() - t0
    return ClaimResult(claim=claim, failures=failures, trials_run=trials_run,
                       sample_failures=sample_failures, upper95_failure_prob=upper,
                       rng_commit=rng_commit, duration_sec=dur)

# ---------- Certificate helpers ----------
def make_certificate(program_hash: str, machine: str, claim_results: List[ClaimResult]) -> BeliefCertificate:
    claims_out = []
    proofs_out = []
    for cr in claim_results:
        c = cr.claim
        claims_out.append({
            "id": c.id,
            "proposition": c.proposition,
            "domain": {"name": c.domain.name, "params": c.domain.params},
            "adversary": c.adversary,
            "oracle": c.oracle,
            "power": {"alpha": c.power_alpha, "trials": c.trials},
            "results": {
                "failures": cr.failures,
                "trialsRun": cr.trials_run,
                "upper95FailureProb": cr.upper95_failure_prob,
                "rngCommit": cr.rng_commit,
                "durationSec": cr.duration_sec
            }
        })
        for p in c.proofs:
            proofs_out.append({"kind": p.kind, "uri": p.uri, "hash": p.hash})
    return BeliefCertificate(
        certVersion="1.0",
        programHash=program_hash,
        machine=machine,
        createdAt=time.time(),
        claims=claims_out,
        proofs=proofs_out
    )

def certificate_hash(cert: BeliefCertificate) -> str:
    blob = json.dumps(asdict(cert), sort_keys=True, separators=(",",":")).encode()
    return "0x" + hashlib.sha256(blob).hexdigest()