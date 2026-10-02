# Independently authored architecture

## Actual Training / Serving

[Observed Qwen training and serving workflow](model-serving.svg) · [Editable flow](model-serving.mmd).
이 도식은 2026-10-02 확인한 실제 학습·adapter·serving 책임을 재구성합니다.
직접 adapter loading은 관측된 경로, merge/apply는 별도 구현 경로입니다.

## Public Experiment Reference

These SVGs and matching Mermaid sources describe generic engineering responsibilities,
not the topology or names of a private platform.

- IMPLEMENTED: implemented in this public sample only.
- PARTIAL: a limited demonstration, not end-to-end verification.
- PROPOSED: reference architecture or future work.

Synthetic/mock describes the data or dependency. PARTIAL nodes with mock tools do not
imply a live external connector; IMPLEMENTED always refers to the offline sample.

Both formats are authored from the same node/edge definitions. SVG is the directly viewable
asset; Mermaid is an editable source, not a claim that a Mermaid renderer produced the SVG.
No company diagrams, screenshot crops, server inventory or scale numbers are included.

- [Parameter-efficient experiment lifecycle](01_experiment_architecture.svg) · [Mermaid](01_experiment_architecture.mmd)
