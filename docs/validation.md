# Local reconstruction validation

Validated: 2026-10-01. Python 3.10.12, standard-library test runner.

- Tests: **16 passed** (11 behavioral + 5 repository-quality) using `python3 -m unittest discover -s tests -v`.
- Default demonstration: executed successfully without production dependencies.
- Scope: synthetic public reconstruction only, not production performance or accuracy.
- File/link/SVG and heuristic disclosure review: no flagged candidate findings at this check.
- Publication status: NEEDS USER REVIEW. IP/NDA and license choice are not validated by tests.

The CPU rank-one experiment and quantized-proxy path were executed.
The real-model PEFT / QLoRA path was **not** trained, dependency-locked or quality-benchmarked.
Its dry-run and validation gates were tested; no model weights were downloaded.
