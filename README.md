# Symbolic Verification of Pruning Rules for Runway Sequencing

This repository accompanies a PATAT 2026 conference submission on the symbolic verification of pruning rules for the Runway Sequencing Problem (RSP). It uses the Z3 SMT solver to encode pruning-rule premises and claims, then checks whether each rule is:

- correct: the premises cannot hold while the claim fails
- non-vacuous: the premises are satisfiable on at least one feasible instance

The notebooks in this repository provide compact, executable proof artefacts for the rules discussed in the paper.

## Repository Contents

- [core/context.py](/Users/tobybenjaminclark/Documents/rsp-smt/core/context.py): symbolic RSP model, including aircraft attributes, separation constraints, sequence-dependent take-off times, and objective expressions.
- [core/checks.py](/Users/tobybenjaminclark/Documents/rsp-smt/core/checks.py): verification routines for correctness and non-vacuity, together with lightweight proof result types.
- [notebooks/complete_orders.ipynb](/Users/tobybenjaminclark/Documents/rsp-smt/notebooks/complete_orders.ipynb): verification notebook for complete-order pruning rules.
- [notebooks/conditional_orders.ipynb](/Users/tobybenjaminclark/Documents/rsp-smt/notebooks/conditional_orders.ipynb): verification notebook for conditional-order pruning rules.
- [requirements.txt](/Users/tobybenjaminclark/Documents/rsp-smt/requirements.txt): minimal Python dependency specification.

## Verification Approach

Each pruning rule is verified in two stages:

1. Non-vacuity check. The solver is asked whether the rule premises are satisfiable together with the foundational constraints of the RSP model. If satisfiable, the solver returns an example witness.
2. Correctness check. The solver is asked whether the premises can hold simultaneously with the negation of the claimed dominance property. If unsatisfiable, the rule is certified as correct.

A rule is reported as `Verified` exactly when both conditions hold: the premises are satisfiable and no counterexample exists.

## Notebooks

### Complete Orders

The complete-order notebook verifies dominance rules for separation-identical aircraft under several objectives:

- delay minimisation, both per-aircraft and total delay
- makespan minimisation
- time-window feasibility preservation

These checks use the canonical pair of sequences

- `S = (ψ₁, i, ψ₂, j, ψ₃)`
- `S' = (ψ₁, j, ψ₂, i, ψ₃)`

which differ only in the relative order of aircraft `i` and `j`.

### Conditional Orders

The conditional-order notebook verifies a conditional dominance rule in which an additional inequality over the objective terms of `i` and `j` is assumed as part of the premises.

## Installation

Create a Python environment and install the dependency:

```bash
pip install -r requirements.txt
```

The current implementation requires:

- Python 3
- `z3-solver 4.16.*`

## Running the Proof Artefacts

Launch Jupyter and open the notebooks:

```bash
jupyter notebook
```

Then run the cells in:

- [notebooks/complete_orders.ipynb](/Users/tobybenjaminclark/Documents/rsp-smt/notebooks/complete_orders.ipynb)
- [notebooks/conditional_orders.ipynb](/Users/tobybenjaminclark/Documents/rsp-smt/notebooks/conditional_orders.ipynb)

Each notebook prints the verification outcome returned by `verify_pruning_rule(...)`.

## Interpretation of Results

The verification code distinguishes four proof-relevant outcomes:

- `Example`: the premises are satisfiable
- `VacuousCertificate`: the premises are unsatisfiable
- `Counterexample`: the premises hold but the claim fails
- `CorrectnessCertificate`: the premises and the negation of the claim are jointly unsatisfiable

At the top level:

- `Verified` means the pruning rule is both correct and non-vacuous
- `Unverified` means either a counterexample exists, the rule is vacuous, or both

## Scope

This repository is intended as a research artefact rather than a production scheduling system. Its purpose is to make the logical structure of the pruning rules explicit, executable, and independently checkable.
