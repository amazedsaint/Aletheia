# Aletheia

An epistemic compiler for computational belief certification through adversarial falsification.

## Overview

Aletheia is a framework for establishing computational trust in software implementations through systematic adversarial testing. It generates cryptographically-verifiable belief certificates that quantify confidence in program correctness based on empirical falsification attempts.

### Key Features

- **Adversarial Testing**: Systematic generation of challenging test cases designed to expose bugs
- **Deterministic Reproducibility**: SHA256-based seed derivation ensures all results can be independently verified
- **Parallel Execution**: Multi-threaded trial runner for efficient large-scale testing
- **Plugin Architecture**: Extensible system for adding new adversaries, oracles, and implementations
- **Belief Certificates**: JSON-based certificates with stable hashing for audit trails
- **On-chain Anchoring**: Solidity contracts for blockchain-based certificate verification
- **Multiple Domains**: Support for different problem domains (sorting, numerical computation, etc.)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/aletheia.git
cd aletheia

# No external dependencies required - uses Python standard library only
python3 --version  # Requires Python 3.8+
```

## Quick Start

### Run a certification test

```bash
# Run with bug detection demo
python -m aletheia.cli compile \
    --seed DEMO-SEED \
    --trials 5000 \
    --workers 4 \
    --out aletheia_certificate.json \
    --show-bug

# Verify the certificate
python -m aletheia.cli verify aletheia_certificate.json
```

### Example Output

```
Bug caught at trial ~4 - example input [3, 4, 3, 1, 5]
Wrote certificate to aletheia_certificate.json
Certificate hash: 0x530d81c335c622c9239475706e77c0c065574405b4941e8eb86550e3617b154f
File sha256: 0xa7b0c6224f52eec7f95ca588ec0a2ba180e91d90b6143327741f45803b54ad8e
```

## Architecture

### Core Components

- **`aletheia/core.py`**: Deterministic runner, epistemic IR, and certificate generation
- **`aletheia/adversaries.py`**: Test case generators (duplicates, nearly-sorted, float vectors)
- **`aletheia/oracles.py`**: Correctness checkers for different domains
- **`aletheia/plugins.py`**: Implementation variants (buggy/fixed quicksort, naive/Kahan dot product)
- **`aletheia/certificate.py`**: Certificate I/O and hashing utilities
- **`aletheia/cli.py`**: Command-line interface

### Epistemic IR

```python
@dataclass
class Claim:
    id: str                    # Unique identifier
    proposition: str           # Human-readable claim
    domain: Domain            # Problem domain specification
    adversary: str            # Test generator name
    oracle: str               # Correctness checker name
    trials: int               # Number of tests to run
    power_alpha: float        # Statistical significance level
```

### Plugin System

Register new components with decorators:

```python
from aletheia.core import register_generator, register_oracle, register_impl

@register_generator("my_adversary")
def my_test_generator(rng: random.Random, params: Dict) -> Any:
    # Generate challenging test cases
    pass

@register_oracle("my_oracle")
def my_correctness_checker(input: Any, output: Any) -> Tuple[bool, Dict]:
    # Return (passed, details)
    pass

@register_impl("my_implementation")
def my_algorithm(input: Any, rng: random.Random) -> Any:
    # Implementation to test
    pass
```

## Supported Domains

### 1. Sorting Correctness
- **Adversary**: Duplicate-heavy and nearly-sorted arrays
- **Oracle**: Verifies sorted order and permutation preservation
- **Implementations**: Buggy quicksort (drops duplicates), 3-way quicksort (correct)

### 2. Numerical Stability
- **Adversary**: Float vectors with extreme magnitude differences
- **Oracle**: Compares against `math.fsum` baseline with relative error tolerance
- **Implementations**: Naive summation, Kahan summation algorithm

## Certificate Format

```json
{
  "certVersion": "1.0",
  "programHash": "0x...",
  "machine": "hostname",
  "createdAt": 1234567890.123,
  "claims": [
    {
      "id": "SortsCorrect@quicksort3",
      "proposition": "quicksort3 sorts correctly...",
      "domain": {"name": "int_array", "params": {...}},
      "adversary": "dup_heavy_small",
      "oracle": "sort_correctness",
      "power": {"alpha": 0.05, "trials": 5000},
      "results": {
        "failures": 0,
        "trialsRun": 5000,
        "upper95FailureProb": 0.0006,
        "rngCommit": "0x843bd0ca...",
        "durationSec": 0.217
      }
    }
  ]
}
```

## On-chain Verification

Solidity contracts for blockchain-based certificate anchoring:

- **`IClaimVerifier.sol`**: Interface for claim verification
- **`SortingClaimVerifier.sol`**: On-chain sorting correctness checker
- **`EvidenceRegistry.sol`**: Certificate submission and challenge system

### Challenge Mechanism

1. Submit certificate hash with bond
2. Challenge window for adversarial refutation
3. If no valid counterexample found, claim finalizes
4. Successful challenges slash the bond

## CI/CD Integration

GitHub Actions workflow included for automated testing:

```yaml
name: aletheia-ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run Aletheia demo
        run: |
          python -m aletheia.cli compile --seed CI-SEED --trials 5000 --out aletheia_certificate.json --show-bug
          python -m aletheia.cli verify aletheia_certificate.json
```

## Development

### Project Structure

```
aletheia/
├── aletheia/              # Core Python package
│   ├── __init__.py
│   ├── core.py           # Main engine
│   ├── adversaries.py    # Test generators
│   ├── oracles.py        # Correctness checkers
│   ├── plugins.py        # Implementations
│   ├── certificate.py    # Certificate utilities
│   ├── anchoring.py      # Blockchain integration
│   └── cli.py            # CLI interface
├── solidity/             # Smart contracts
│   ├── IClaimVerifier.sol
│   ├── SortingClaimVerifier.sol
│   └── EvidenceRegistry.sol
├── .github/workflows/    # CI configuration
│   └── ci.yml
├── README.md
├── LICENSE
└── .gitignore
```

### Running Tests

```bash
# Basic test
python -m aletheia.cli compile --seed TEST --trials 1000 --workers 2 --out test.json

# Verify reproducibility
python -m aletheia.cli compile --seed TEST --trials 1000 --workers 2 --out test2.json
diff test.json test2.json  # Should be identical

# Performance test
python -m aletheia.cli compile --seed PERF --trials 100000 --workers 8 --out perf.json
```

## Theory

Aletheia applies Karl Popper's falsificationism to software verification. Instead of proving correctness, it seeks to:

1. **Generate adversarial inputs** likely to expose bugs
2. **Run empirical trials** to attempt falsification
3. **Quantify confidence** using statistical bounds (Rule of Three)
4. **Create audit trails** via deterministic, reproducible certificates

The system provides a "proof of exhaustive search for counterexamples" rather than formal proof of correctness.

## Contributing

Contributions welcome! Areas of interest:

- New problem domains and adversaries
- Formal verification integration (TLA+, Coq, Lean)
- Advanced statistical methods (Bayesian updating, sequential testing)
- Performance optimizations
- Additional blockchain platforms

## License

MIT License - see LICENSE file for details

## Citation

If you use Aletheia in your research, please cite:

```bibtex
@software{aletheia2024,
  title = {Aletheia: An Epistemic Compiler for Computational Belief Certification},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/aletheia}
}
```

## Contact

- Issues: [GitHub Issues](https://github.com/yourusername/aletheia/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/aletheia/discussions)