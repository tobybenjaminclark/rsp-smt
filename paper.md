
# Automated Verification of Pruning Rules for Runway Sequencing

> **Toby Clark, Jason Atkin, Geert De Maere** \
> School of Computer Science, University of Nottingham, UK

 **Abstract:** Exact approaches to the Runway Sequencing Problem (RSP)
rely on pruning rules to make optimisation tractable. However, these
rules are typically proven manually, making it difficult to evaluate new
candidates or transport across problem variants. We present an SMT-
based framework for automatically verifying pruning rules for the RSP.
We verify several published pruning rules within a symbolic sequence ab-
straction, where correctness corresponds to refuting all counterexamples,
supporting a more systematic workflow for developing pruning rules.

 **Keywords:** Runway Sequencing · Pruning Rules · Verification · Exact
Optimisation · Satisfiability Modulo Theories (SMT) · Formal Methods

### Introduction

Runway Sequencing is an important online timetabling problem at congested airports, where the efficient use of runways has a direct impact on delay propagation, emissions, and operational cost. Despite the NP-hardness of the general formulation, practical runway sequencing instances possess structural characteristics in their separation constraints and objective functions that can be systematically exploited, enabling the application of exact solution methods. 

One approach to solving these defines a set of pruning rules, which eliminate partial sequences that are provably dominated by other partial sequences. These leverage structural characteristics of the problem constraints to reduce time complexity but rely on manual proofs to certify they preserve optimal solutions. However, manual reasoning is tightly coupled to a specific formulation, making rules difficult to transport across variants with differing constraints or assumptions. Even small model changes can invalidate a pruning rule, necessitating a human review to re-prove rule correctness under the new model.

We propose the use of Satisfiability Modulo Theories (SMT) for verifying the correctness of such rules. SMT extends Boolean satisfiability with constructs such as linear arithmetic, to enable automated verification of pruning rules. Specifically, we use Z3 Theorem Prover to provide the first machine-executable formalization that such rules preserve correctness, and demonstrate how operational runway sequencing constraints can be translated into a logically verifiable representation, and checked programmatically.

---

### Pruning Rules in Optimisation

Several optimisation algorithms (e.g. dynamic programming, branch and bound, tree search) incrementally construct partial solutions and extend them until a complete solution is found. Pruning rules define dominance relations over partial solutions, enabling the early elimination of inferior search branches, without compromising optimality.

Whilst pruning rules are not optimisers in themselves, a single correctness proof is orthogonal to the choice of search strategy, enabling their safe reuse across many algorithmically-independent search procedures.

> **Pruning Rules for Runway Sequencing.** De Maere et al. introduced a set of pruning rules for the RSP, reducing time complexity from $O(n!)$ to $O(N^2(n+1)^N)$ without compromising optimality, where $N$ denotes the distinct types of aircraft. Variants of these principles are currently employed in runway sequencing systems at London Heathrow Airport (LHR), highlighting their real world relevance.\
> \
> These are derived from structural properties of wake-separation constraints and time-window feasibility, and induce a dominance relation over partial sequences. More broadly, pruning rules have received considerable attention in machine scheduling literature, often used in exact methodologies

> **Logical Structure & Correctness.** Pruning rules can be viewed as logical implications: their preconditions specify when the rule may be applied to a partial solution, and their postcondition states that the pruned branch cannot yield a better feasible completion with respect to some objective component. \
> \
> Rules are correct if this implication holds for all feasible instances. Equivalently, whenever the preconditions are satisfied, every feasible completion of the pruned branch is dominated by some feasible completion of the retained branch.

### Contributions

We propose the use of Satisfiability Modulo Theories to automatically verify pruning rules for the Runway Sequencing Problem (RSP), including several rules introduced by De Maere et. al. In addition to the theoretical contributions outlined below, we implement the framework using the Z3 Theorem Prover and make available executable notebooks that reproduce all verification results.
- We formalise the implicit and explicit semantics of the RSP in SMT.
- We develop a refutation-based SMT framework for verifying pruning rules.
- We machine verify several of the pruning rules introduced by De Maere et. al.
- We propose a counterexample-preserving abstraction for runway sequencing.

Our contribution is therefore not a new pruning rule, but a reusable SMT formulation for automatically verifying complete and conditional order pruning rules in the context of the Runway Sequencing Problem.

---
