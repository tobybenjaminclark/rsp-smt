
# Automated Verification of Pruning Rules for Runway Sequencing

> **Toby Benjamin Clark, Jason Atkin, Geert De Maere** \
> School of Computer Science, University of Nottingham, UK

 **Abstract:** Exact approaches to the Runway Sequencing Problem (RSP) rely on pruning rules to make optimisation tractable. However, these rules are typically proven manually,
 making it difficult to evaluate new candidates or reuse rules across problem variants. We propose the use of Satisfiability Modulo Theories to automatically verify pruning rules
 for the RSP. Our approach verifies several published complete and conditional order pruning rules within a symbolic sequence abstraction, where correctness is established by
 refuting all counterexamples. This enables a more systematic and reusable workflow for iterative pruning rule development, and provides a basis for future automated rule synthesis.

 **Keywords:** Runway Sequencing · Pruning Rules · Verification · Exact
Optimisation · Satisfiability Modulo Theories (SMT) · Formal Methods

---


This repository accompanies a PATAT 2026 conference submission on the automated verification of pruning rules for the Runway Sequencing Problem (RSP). It uses the Z3 Theorem Prover
(SMT Solver) to verify that pruning rules are both correct (never prune optimal solutions) and non-vacuous (premises are satisfiable in at least one feasible instance). Our approach
is implemented in `core/` with accompanying encodings of pruning rules contained in `notebooks/`. The notebooks in this repository provide compact, executable proof artefacts for
the rules discussed in the paper. This repository is intended as a research artefact rather than a production scheduling system. Its purpose is to make the logical structure of the pruning rules explicit, executable, and independently checkable.


### Repository Contents

- [core/context.py](core/context.py): symbolic RSP model, including aircraft attributes, separation constraints, sequence-dependent take-off times, and objective expressions.
- [core/checks.py](core/checks.py): verification routines for correctness and non-vacuity, together with lightweight proof result types.
- [notebooks/complete_orders.ipynb](notebooks/complete_orders.ipynb): verification notebook for complete-order pruning rules.
- [notebooks/conditional_orders.ipynb](notebooks/conditional_orders.ipynb): verification notebook for conditional-order pruning rules.
- [notebooks/additional_orders.ipynb](notebooks/additional_orders.ipynb): verification notebook for additional conditional-order pruning rules.

### Installation

All requirements are provided in `requirements.txt` and can be installed as follows. All verification encodings were developed in Python, using version 3.14. Replicability may be
affected if a different Python environment version is used.

```bash
pip install -r requirements.txt
```

To run verification of pruning rules, launch Jupyter and open the notebooks:

```bash
jupyter notebook
```

Then run the individual cells in:

- [notebooks/complete_orders.ipynb](notebooks/complete_orders.ipynb)
- [notebooks/conditional_orders.ipynb](notebooks/conditional_orders.ipynb).
- [notebooks/additional_orders.ipynb](notebooks/additional_orders.ipynb)

#### Interpretation of Results

The verification code distinguishes four proof-relevant outcomes:

- `Example`: the premises are satisfiable
- `VacuousCertificate`: the premises are unsatisfiable
- `Counterexample`: the premises hold but the claim fails
- `CorrectnessCertificate`: the premises and the negation of the claim are jointly unsatisfiable

At the top level:

- `Verified` means the pruning rule is both correct and non-vacuous
- `Unverified` means either a counterexample exists, the rule is vacuous, or both

#### Example Cell

The cell below encodes a complete-order pruning rule as an SMT problem. It constructs two symbolic sequences that differ only by swapping aircraft `i` and `j`, states the rule premises as Z3 constraints, and asks whether the makespan claim follows.

```python
from core.context import *
from core.checks import *

# Construct the two sequences that differ only in the relative order of i and j.
S1, S2, ctx = get_sequences()

# State the premises: order the release times and require i and j to be separation-equivalent.
premises = [
    ctx.r["i"] <= ctx.r["j"],   *ctx.separation_equivalence("i", "j"),
]

# Verify that the makespan of S1 is no larger than that of S2.
claim = S1.makespan <= S2.makespan

# Ask the solver to certify the claim.
res = verify_pruning_rule(ctx, premises, claim)
print(f"\nComplete Order Makespan: {res}\n")
```

The log output records the two solver checks: one for non-vacuity and one for correctness. The final result then reports whether both checks succeeded. Both the logs and result for this check are shown below.

>`[12:00:00]` Building default sequence pair with ψ-count = 2 \
`[12:00:00]` Creating RSP context for 8 aircraft \
`[12:00:00]` Checking non-vacuity with 9 premises and 136 foundational constraints \
`[12:00:00]` Finished solver check for non-vacuity (sat, took 3ms) \
`[12:00:00]` Checking correctness with 9 premises and 136 foundational constraints \
`[12:00:00]` Finished solver check for correctness (unsat, took 70ms) \
\
**Complete Order Makespan: Verified**
