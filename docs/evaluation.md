# Evaluation

11 behavioral tests exercise the sample contracts. Five repository-quality tests
exercise the scanner, not model performance. Run `python3 -m unittest discover -s tests -v`.

The target is deliberately easy and rank-one, not a language benchmark. Uniform 4-bit rounding is not NF4/QLoRA or a memory-saving implementation. Optional PEFT execution and dependency compatibility are unvalidated.

Future evaluation needs independently labeled tasks and separated baselines.
A synthetic regression pass rate is not a real-world quality score.
