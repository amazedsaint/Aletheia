import argparse, platform, os
from typing import List
from . import adversaries, oracles, plugins  # ensure registries are populated
from .core import Claim, Domain, parallel_trials, make_certificate, certificate_hash, BeliefCertificate
from .certificate import save_certificate, load_certificate, sha256_hex

def build_demo_claims(trials: int) -> List[Claim]:
    c1=Claim(id="SortsCorrect@quicksort3", proposition="quicksort3 sorts correctly on small duplicate-heavy arrays",
             domain=Domain(name="int_array", params={"nmin":0,"nmax":12,"range":(0,9)}),
             adversary="dup_heavy_small", oracle="sort_correctness", trials=trials, power_alpha=0.05, stop_on_first_failure=True)
    c2=Claim(id="DotKahanCorrect@floatmix", proposition="kahan dot approximates fsum within 1e-6 rel. error under magnitude mixing",
             domain=Domain(name="float_dot", params={"nmin":64,"nmax":1024,"hi":1e16,"lo":1e-16}),
             adversary="float_dot_vectors", oracle="dot_correctness", trials=trials, power_alpha=0.05, stop_on_first_failure=True)
    return [c1, c2]

def cmd_compile(args):
    claims=build_demo_claims(trials=args.trials)
    results=[]
    if args.show_bug:
        bad=parallel_trials(claims[0], "buggy_quicksort", args.seed, max_workers=args.workers)
        if bad.failures:
            print(f"Bug caught at trial ~{bad.sample_failures[0].idx} - example input {bad.sample_failures[0].input_data}")
        else:
            print("Warning: buggy impl unexpectedly passed")
        bad2=parallel_trials(claims[1], "dot_naive", args.seed, max_workers=args.workers)
        if bad2.failures:
            f=bad2.sample_failures[0]
            print(f"Naive dot deviated - observed {f.details.get('observed')} vs baseline {f.details.get('baseline')}")
        else:
            print("Naive dot passed within tolerance on sampled trials")
    res1=parallel_trials(claims[0], "quicksort3", args.seed, max_workers=args.workers)
    res2=parallel_trials(claims[1], "dot_kahan", args.seed, max_workers=args.workers)
    results.extend([res1, res2])
    program_hash = "0x"+os.urandom(32).hex() if args.program_hash is None else args.program_hash
    cert=make_certificate(program_hash, platform.node(), results)
    out=args.out or "aletheia_certificate.json"
    save_certificate(cert, out)
    print("Wrote certificate to", out)
    print("Certificate hash:", certificate_hash(cert))
    print("File sha256:", sha256_hex(out))
    return 0

def cmd_verify(args):
    data=load_certificate(args.path)
    cert=BeliefCertificate(certVersion=data["certVersion"], programHash=data["programHash"], machine=data["machine"], createdAt=data["createdAt"], claims=data["claims"], proofs=data.get("proofs",[]))
    print("Computed certificate hash:", certificate_hash(cert))
    print("File sha256:", sha256_hex(args.path)); return 0

def main(argv=None):
    p=argparse.ArgumentParser(prog="aletheia", description="Aletheia epistemic compiler POC")
    sub=p.add_subparsers(dest="cmd")
    p_compile=sub.add_parser("compile", help="Run tests and emit certificate")
    p_compile.add_argument("--seed", required=True); p_compile.add_argument("--trials", type=int, default=20000)
    p_compile.add_argument("--workers", type=int, default=0); p_compile.add_argument("--out", default="aletheia_certificate.json")
    p_compile.add_argument("--program-hash", dest="program_hash"); p_compile.add_argument("--show-bug", action="store_true")
    p_compile.set_defaults(func=cmd_compile)
    p_verify=sub.add_parser("verify", help="Recompute hashes for an existing certificate")
    p_verify.add_argument("path"); p_verify.set_defaults(func=cmd_verify)
    args=p.parse_args(argv)
    if not hasattr(args,"func"): p.print_help(); return 2
    return args.func(args)

if __name__=="__main__":
    raise SystemExit(main())