from __future__ import annotations
from dataclasses import dataclass
from time import perf_counter
from typing import Optional
from core.context import RSPContext
from z3 import BoolRef, CheckSatResult, ModelRef, Not, Solver, sat, unsat
from core.format import PrintableRSPModel
from core.log import get_logger


log = get_logger(__name__)

# Define a type alias to differentiate models in RSP from general Z3 models.
RSPModelRef = ModelRef

# Define a satisfiable Z3 model relevant to pruning-rule verification.
@dataclass(frozen=True)
class RSPSatModel(PrintableRSPModel):
    model: RSPModelRef

# Define a model witnessing that the premises are satisfiable.
@dataclass(frozen=True)
class Example(RSPSatModel):
    pass

# Define a model witnessing that the premises hold while the claim fails.
@dataclass(frozen=True)
class Counterexample(RSPSatModel):
    pass





# Define a base class for unsatisfiability-based certificates.
@dataclass(frozen=True)
class Certificate:
    check: CheckSatResult

    def __post_init__(self) -> None:
        if self.check != unsat:
            raise ValueError(f"{type(self).__name__} requires check == unsat")

# Define a certificate that `premises ∧ ¬claim` is unsatisfiable, so the rule is sound.
@dataclass(frozen=True)
class CorrectnessCertificate(Certificate):
    pass

# Define a certificate that `premises` is unsatisfiable, so the rule never fires.
@dataclass(frozen=True)
class VacuousCertificate(Certificate):
    pass





def _check_solver(solver: Solver, label: str) -> CheckSatResult:
    start = perf_counter()
    res = solver.check()
    elapsed_ms = round((perf_counter() - start) * 1000)
    log.info("Finished solver check for %s (%s, took %dms)", label, res, elapsed_ms)
    return res


# Define a function to check whether the premises of a pruning rule are satisfiable.
def check_non_vacuous(ctx: RSPContext, premises: [BoolRef]) -> VacuousCertificate | Example:
    premises = list(premises)
    all_premises = premises + ctx.foundational_constraints
    log.info("Checking non-vacuity with %d premises and %d foundational constraints", len(premises), len(ctx.foundational_constraints))
    s: Solver = Solver()
    s.add(*all_premises)
    res = _check_solver(s, "non-vacuity")

    if res == sat:      return Example(s.model())
    if res == unsat:    return VacuousCertificate(res)
    raise RuntimeError(f"Unexpected solver result: {res}")



# Define a function to check whether a pruning rule is logically correct.
def check_correct(ctx: RSPContext, premises: [BoolRef], claim: BoolRef) -> CorrectnessCertificate | Counterexample:
    premises = list(premises)
    all_premises = premises + ctx.foundational_constraints
    log.info("Checking correctness with %d premises and %d foundational constraints", len(premises), len(ctx.foundational_constraints))
    s: Solver = Solver()
    s.add(*all_premises)
    s.add(Not(claim))
    res = _check_solver(s, "correctness")

    if res == unsat:    return CorrectnessCertificate(res)
    if res == sat:      return Counterexample(s.model())
    raise RuntimeError(f"Unexpected solver result: {res}")




# Define a class that contains both the correctness certificate, and feasible example for a pruning rule,
# meaning that the pruning rule has been verified.
@dataclass(frozen=True)
class Verified:
    correctness: CorrectnessCertificate
    example: Example

    @property
    def is_correct(self) -> bool:       return True

    @property
    def is_non_vacuous(self) -> bool:   return True
    def __repr__(self) -> str:          return f"{type(self).__name__}"



# Define a class that contains either/both of a pruning rule counterexample, and vacuity certificate,
# meaning that the pruning rule is invalid.
@dataclass(frozen=True)
class Unverified:
    counterexample:      Optional[Counterexample]      = None
    vacuous_certificate: Optional[VacuousCertificate]  = None

    def __post_init__(self) -> None:
        if self.counterexample is None and self.vacuous_certificate is None:
            raise ValueError("Unverified must contain a counterexample, a vacuity certificate, or both")

    @property
    def is_correct(self) -> bool:       return False

    @property
    def is_non_vacuous(self) -> bool:   return self.vacuous_certificate is None

    def __repr__(self) -> str:
        return (
            f"Unverified(counterexample = {'yes' if self.counterexample is not None else 'no'}, "
            f"vacuous = {'yes' if self.vacuous_certificate is not None else 'no'})"
        )



# Define a function to verify a pruning rule is both correct and non-vacuous.
def verify_pruning_rule(ctx, premises: [BoolRef], claim: BoolRef) -> Verified | Unverified:
    premises = list(premises)

    # Invoke checks for rule correctness and non-vaccuity.
    non_vacuity = check_non_vacuous(ctx, premises)
    correctness = check_correct(ctx, premises, claim)

    # If we are able to verify the rule triggers in at least one feasible instance, and is correct,
    # the pruning rule is verified. (Therefore, return the Verified object).
    if isinstance(non_vacuity, Example) and isinstance(correctness, CorrectnessCertificate):
        return Verified(
            correctness=correctness,
            example=non_vacuity,
        )

    # Otherwise, there was either a counterexample or it was vacuous, so return Unverified.
    return Unverified(
        counterexample=correctness if isinstance(correctness, Counterexample) else None,
        vacuous_certificate=non_vacuity if isinstance(non_vacuity, VacuousCertificate) else None,
    )
