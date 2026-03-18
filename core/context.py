from dataclasses import dataclass
from functools import cached_property, reduce
from itertools import product
from z3 import *




# Define parameters
ω1, ω2, ω3, ω4 = RealVal(1), RealVal(2), RealVal(3), RealVal(4)
W1, W2 = RealVal(1), RealVal(1)
α = RealVal(1)



# Define symbolic maximum operator over pairs and extend to finite lists.
def zmax(x: ArithRef, y: ArithRef) -> ArithRef:     return If(x >= y, x, y)
def zmax_list(xs: [ArithRef]) -> ArithRef:          return reduce(zmax, xs)




# Define a class to store Z3 variables related to the Runway Sequencing Problem,
# stores per aircraft variables, such as release time, base time, queue time ...
@dataclass(frozen=True)
class RSPContext:
    aircraft: tuple
    r: dict
    b: dict
    c: dict
    ec: dict
    lc: dict
    et: dict
    lt: dict
    delta: dict

    # Define a method to enforce all aircraft attributes and δ-separations to be non-negative.
    @property
    def variable_constraints(self):
        return [
            # Enforces that every aircraft attribute is non-negative / ≥ 0
            *[p[ac] >= 0 for ac in self.aircraft for p in (self.r, self.b, self.c, self.ec, self.lc, self.et, self.lt)],

            # Enforces that all δ-separations are non-negative / ≥ 0
            *[self.delta[(x, y)] >= 0 for x, y in product(self.aircraft, self.aircraft)]
        ]

    # Define a method to enforce time windows as total orders (i.e. start time is strictly less than the end time)
    @property
    def ordered_window_constraints(self):
        return [
            And(self.et[ac] < self.lt[ac], self.ec[ac] < self.lc[ac]) for ac in self.aircraft
        ]

    # Define a method to fix release time as the maximum of base time, and time slot start times.
    @property
    def release_time_constraints(self):
        return [
            self.r[ac] == zmax(self.b[ac] + self.c[ac], zmax(self.et[ac], self.ec[ac])) for ac in self.aircraft
        ]

    # Define a method to conjoin all foundational constraints.
    @cached_property
    def foundational_constraints(self):
        return (
            self.variable_constraints
            + self.ordered_window_constraints
            + self.release_time_constraints
        )


    # Define a method to enfoce that two aircraft are δ-equivalent (identical separation requirements)
    def separation_equivalence(self, i: str, j: str):
        # Enforce that i & j have positive, identical separation requirements in regard to each other.
        internal_constraint = [
            self.delta[(i, j)] > 0, self.delta[(j, i)] > 0,
            self.delta[(i, j)] == self.delta[(j, i)],
        ]

        # Enforce that i & j have identical separation requirements in regard to all other aircraft.
        external_constraint = [
            And(self.delta[(i, x)] == self.delta[(j, x)], self.delta[(x, i)] == self.delta[(x, j)]) for x in filter(lambda k: k not in (i, j), self.aircraft)
        ]
        return [*internal_constraint, *external_constraint]

    def with_sequence(self, seq) -> RSPSequenceContext:
        return RSPSequenceContext(self, tuple(seq))




# Constructor for RSPContext
def make_context(aircraft: [str]) -> RSPContext:
    aircraft = tuple(aircraft)
    return RSPContext(
        aircraft =   aircraft,
        r =          {ac: Real(f"r-{ac}") for ac in aircraft},
        b =          {ac: Real(f"b-{ac}") for ac in aircraft},
        c =          {ac: Real(f"c-{ac}") for ac in aircraft},
        ec =         {ac: Real(f"ec-{ac}") for ac in aircraft},
        lc =         {ac: Real(f"lc-{ac}") for ac in aircraft},
        et =         {ac: Real(f"et-{ac}") for ac in aircraft},
        lt =         {ac: Real(f"lt-{ac}") for ac in aircraft},
        delta =      {(x, y): Real(f"δ-{x}{y}") for x, y in product(aircraft, aircraft)},
    )




# Define a class to handle and generate variables related to a sequence (fixed ordering) of aircraft within
# a given RSP context. The provided sequence must be a permutation of the aircraft in the base RSPContext.
@dataclass(frozen=True)
class RSPSequenceContext:
    ctx: RSPContext
    seq: tuple

    # Define a check to enforce that the given sequence is a corret permutation of aircraft.
    def __post_init__(self):
        if set(self.seq) != set(self.ctx.aircraft):
            raise ValueError("Sequence must be a permutation of base.aircraft")


    # Define a property to access takeoff times (since these are sequence dependent)
    @cached_property
    def takeoff(self):
        seq = self.seq
        T = {seq[0]: self.ctx.r[seq[0]]}
        for k in range(1, len(seq)):
            preds = seq[:k]
            T[seq[k]] = zmax(
                self.ctx.r[seq[k]],
                zmax_list([T[x] + self.ctx.delta[(x, seq[k])] for x in preds]),
            )
        return T

    # Define a property to access per-aircraft delay costs (since these are sequence dependent)
    @cached_property
    def delay(self):
        return {ac: W1 * ((self.takeoff[ac] - self.ctx.b[ac]) ** α) for ac in self.seq}

    # Define a property to access per-aircraft CTOT penalties (since these are sequence dependent)
    @cached_property
    def ctot(self):
        def C(t, lc) -> ArithRef: return W2 * If(t <= lc, RealVal(0), If(t <= lc + 300, ω1 * (t - lc) + ω2, ω3 * (t - lc) + ω4))
        return {ac: C(self.takeoff[ac], self.ctx.lc[ac]) for ac in self.seq }

    # Define a property to access makespan (highest takeoff time in sequence)
    @cached_property
    def makespan(self):
        return zmax_list([
            self.takeoff[x] for x in self.ctx.aircraft
        ])

    # Define a property to access whether or not a aircraft meets its hard time window.
    @cached_property
    def window_violation(self):
        return {ac: self.takeoff[ac] > self.ctx.lt[ac] for ac in self.seq}

    # Define a method to enforce that a sequence is time window feasible.
    @cached_property
    def time_window_feasible(self):
        return [
            self.takeoff[ac] <= self.ctx.lt[ac] for ac in self.seq
        ]




# Define a function to retrieve 2 sequences, differing only by the swapping the positions of
# aircraft i and j. Also provides the RSPContext for access to aircraft attributes.
def get_sequences() -> (RSPSequenceContext, RSPSequenceContext, RSPContext):
    aircraft = ["ψ₁", "i", "ψ₂", "j", "ψ₃"]
    ctx = make_context(aircraft)
    S1 = ctx.with_sequence(["ψ₁", "i", "ψ₂", "j", "ψ₃"])
    S2 = ctx.with_sequence(["ψ₁", "j", "ψ₂", "i", "ψ₃"])
    return S1, S2, ctx