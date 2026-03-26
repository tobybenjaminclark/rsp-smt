from __future__ import annotations
from rich.console import Console
from rich.table import Table
from z3 import AlgebraicNumRef, ModelRef, RatNumRef, is_false, is_rational_value, is_true, simplify
from core.context import RSPContext, RSPSequenceContext



# Define a helper to render Z3 values in a compact, readable form.
def _render_value(model: ModelRef, expr) -> str:
    value = simplify(model.evaluate(expr, model_completion=True))
    if is_true(value):                      return "True"
    if is_false(value):                     return "False"
    if is_rational_value(value):            return f"{value.numerator_as_long() / value.denominator_as_long():.2f}"
    if isinstance(value, RatNumRef):        return f"{value.numerator_as_long() / value.denominator_as_long():.2f}"
    if isinstance(value, AlgebraicNumRef):  return f"{float(value.approx(20).as_fraction()):.2f}"
    return str(value)



# Define a helper to print a Rich table.
def _print_table(title: str, headers: [str], rows: [[str]]) -> None:
    table = Table(title=title)
    for header in headers:  table.add_column(header)
    for row in rows:        table.add_row(*[str(cell) for cell in row])
    Console().print(table)



# Define a function to print the aircraft-level variables stored in an RSP model.
class PrintableRSPModel:
    def print_model(self: "RSPSatModel", ctx: RSPContext, sequences: [RSPSequenceContext]) -> None:
        model = self.model

        _print_table(
            "Aircraft",
            ["Aircraft", "Release Time (rᵢ)", "Base Time (bᵢ)", "Queue Time (cᵢ)", "CTOT Start (ecᵢ)", "CTOT End (lcᵢ)", "Time Window Start (etᵢ)", "Time Window End (ltᵢ)"],
            [[ac, *[_render_value(model, p[ac]) for p in (ctx.r, ctx.b, ctx.c, ctx.ec, ctx.lc, ctx.et, ctx.lt)]] for ac in ctx.aircraft],
        )

        if sequences:
            sequence_rows = []
            label_width = max(len(ac) for seq in sequences for ac in seq.seq)
            for idx, seq in enumerate(sequences, start=1):
                seq_label = "S" if idx == 1 else "S'"
                sequence_rows.extend([[
                    f"{ac.ljust(label_width)} ({seq_label})",
                    _render_value(model, seq.takeoff[ac]),      _render_value(model, seq.delay[ac]),
                    _render_value(model, seq.ctot[ac]),         _render_value(model, seq.window_violation[ac]),
                ] for ac in seq.seq])
                if idx != len(sequences):   sequence_rows.append(["", "", "", "", ""])

            _print_table(
                "Sequences",
                ["Aircraft", "Takeoff Time (tᵢ)", "Delay Cost", "CTOT Cost", "Window Violation"],
                sequence_rows,
            )

        _print_table(
            "Separation Matrix",
            ["Leading / Trailing", *ctx.aircraft],
            [[x, *[_render_value(model, ctx.delta[(x, y)]) for y in ctx.aircraft]] for x in ctx.aircraft],
        )
