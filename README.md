# Aletheia: An Epistemic Compiler

> *"Evidence matters more than folklore."*

Most compilers take your code on faith. They assume that what you wrote is true - that your sort function actually sorts, that your optimization really makes things faster. But in reality every function is a claim about the world.

- "This sorts correctly."
- "This controller stabilizes the system."
- "This algorithm is faster on nearly-sorted data."

**An epistemic compiler flips the default.** It treats code as hypotheses - falsifiable claims - and refuses to emit binaries until the evidence holds up.

## Core Concept

Instead of just checking syntax and types, an epistemic compiler:

1. **Treats functions as hypotheses** - Every function must declare its assumptions and test adversaries
2. **Runs adversarial testing** - Attempts to falsify claims before compilation
3. **Quantifies belief** - Emits binaries with belief certificates showing confidence levels
4. **Makes evidence-driven decisions** - Selects algorithms based on actual performance data, not folklore

## Quick Start

```bash
# Run the epistemic compiler
python aletheia_epicompiler.py

# This will:
# 1. Test buggy vs correct sorting implementations
# 2. Compare performance on different input distributions
# 3. Generate a belief certificate with quantified confidence
```

## How It Works

### 1. Epistemic Primitives

The language is extended with epistemic primitives:

```python
conjecture SortsCorrect
assume Domain: length in 0..12
claim φ: is_sorted(qs3(a)) && is_permutation(a, qs3(a))
refute with adversary DuplicatesBiased
power α=0.05, budget=20_000
```

### 2. Adversarial Testing

Instead of assuming correctness, the compiler actively tries to break your code:

```python
# The compiler generates adversarial inputs
[0, 8, 3, 0, 1, 6, 6, 1, 3]  # Duplicate-heavy array

# Buggy quicksort output (drops duplicates):
[0, 1, 3, 6, 8]  # REJECTED - Build fails!

# Fixed quicksort output:
[0, 0, 1, 1, 3, 3, 6, 6, 8]  # ACCEPTED - Evidence holds
```

### 3. Performance Claims

The compiler doesn't just check correctness - it verifies performance claims:

```python
# Folklore: "Quicksort is better on nearly-sorted inputs"
# Reality: After 1200 trials, mergesort consistently wins

# Compiler synthesizes new rule based on evidence:
if nearly_sorted(a):
    use mergesort
elif distinctness_ratio(a) < 0.03:
    use quicksort3
else:
    use mergesort
```

### 4. Belief Certificates

Every compiled binary comes with a belief certificate:

```
Claim A (Correctness): quicksort_3way sorts correctly
- Falsification budget: 20,000 tests
- Result: 0 failures observed
- Conservative 95% upper bound on failure probability: 0.00015
- Verdict: Emit (claim holds at tested power)

Claim B (Performance): On nearly-sorted arrays...
- Result: Refuted (posterior mean 0.326, P(p>0.5)=0.001)
- Action: Specialize to mergesort for nearly-sorted inputs
```

## Architecture

The epistemic compilation pipeline:

```
Source Code → Parse → Extract Claims → Generate Adversaries
                                              ↓
    Emit Binary ← Update Beliefs ← Test Claims
         +
    Certificate
```

Key components:

- **BetaBernoulliClaim**: Maintains Bayesian posterior for success probability
- **Adversarial Generators**: Create challenging test cases (duplicates, nearly-sorted, etc.)
- **Falsification Engine**: Attempts to find counterexamples
- **Performance Comparator**: Empirically compares algorithm variants
- **Certificate Generator**: Documents evidence and decisions

## Example Output

Running the compiler on sorting algorithms:

```bash
$ python aletheia_epicompiler.py

Aletheia prototype run complete in 2.847s
bug_found_at_trial: 3
bug_counterexample: [0, 8, 3, 0, 1, 6, 6, 1, 3]
fixed_tests_run: 20000
fixed_upper_95_bound: 0.00015
nearly_sorted_posterior_mean_success: 0.326
nearly_sorted_prob_better: 0.001
rho_threshold: 0.03
certificate_path: ./aletheia_certificate.md
```

## Applications

### AI/ML
- Models come with quantified risk assessments
- Training claims are verified, not assumed
- Deployment decisions based on evidence

### Robotics
- Controllers shipped with validation protocols
- Safety claims verified in simulation before deployment
- Performance guarantees backed by data

### Finance/Biotech
- Trading strategies with belief certificates
- Clinical protocols with evidence trails
- Risk quantification built into the compilation

## Philosophy

Traditional compilers are **assumption machines** - they trust that your code does what you claim.

Epistemic compilers are **evidence machines** - they verify claims and quantify confidence.

This isn't just about catching bugs. It's about changing how we think about code - from assertions we make to hypotheses we test.

## Implementation Details

The prototype (`aletheia_epicompiler.py`) demonstrates:

1. **Falsification-first compilation** for correctness claims
2. **Bayesian updating** for performance beliefs
3. **Adversarial test generation** with multiple strategies
4. **Belief certificate emission** with quantified confidence

All in pure Python with no external dependencies.

## Future Work

- Extend to more complex claims (memory usage, concurrency safety)
- Integrate with formal verification for stronger guarantees
- Build IDE support for epistemic annotations
- Create domain-specific adversaries for different applications
- Develop epistemic type systems

## License

MIT

---

*"Instead of shipping assumptions, you ship evidence. That's the leap - turning compilers from assumption-machines into epistemic-machines."*