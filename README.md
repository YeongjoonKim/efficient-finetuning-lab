# Efficient Fine-tuning Lab

## 01 Overview

An executed CPU experiment learns a rank-one adapter around a frozen synthetic linear model. A **separate, unexecuted** PEFT recipe describes opt-in public-model LoRA/QLoRA. **11 behavioral tests** validate the toy learning loop and execution gates; they do not measure language-model improvement.

This repository is a sanitized and reconstructed technical showcase based on engineering experience from a private production AI platform.
It does not contain proprietary source code, private data, internal APIs, or production configuration.

본 저장소는 비공개 운영 AI 시스템의 설계·개발 경험을 기반으로 독립 재구성한 공개 기술 예제입니다. 회사 소스, 비공개 데이터, 내부 API 및 운영 설정은 포함하지 않습니다.

## 02 Problem

Parameter-efficient training needs a clear account of what changed, which data was held out and what can actually be reproduced. Configuration alone is not experimental evidence.

## 03 Architecture

![Reference architecture](docs/architecture/01_experiment_architecture.svg)

[Editable Mermaid and diagram scope](docs/architecture/README.md).
Statuses are **IMPLEMENTED / PARTIAL / PROPOSED**; synthetic/mock describes the
dependency or data, not an additional implementation status.

## 04 Key Engineering Decisions

Separate executed CPU low-rank learning from unexecuted model recipes. Freeze the base, separate train/holdout inputs and hash artifacts. Gate optional execution on revision, license acknowledgement and local weights.

[Design decisions](docs/design-decisions.md).

## 05 Implementation

IMPLEMENTED: analytic CPU gradient updates, 8 trainable vs 16 frozen parameters, separate deterministic train/holdout sets and base/checkpoint hashes. PARTIAL: optional PEFT training recipe, dry-run and gate-tested only. PROPOSED: pinned dependency environment, executed public-model experiment and task-level/resource comparison.

The uniform 4-bit rounding proxy is **not NF4, double quantization or QLoRA**, and does not pack tensors or demonstrate memory savings.

The optional candidate is [Qwen2.5-0.5B](https://huggingface.co/Qwen/Qwen2.5-0.5B).
Review its Apache-2.0 model card and exact revision terms. Optional execution requires
a full 40-character revision, cached public safetensors and explicit license acknowledgement;
remote code and downloads are disabled. LoRA uses a frozen base; the QLoRA recipe uses
NF4, double quantization and PEFT preparation following the
[official guide](https://huggingface.co/docs/peft/developer_guides/quantization).
Dependencies are torch, transformers, peft and (QLoRA) bitsandbytes. **No tested lockfile
or model execution is supplied.** QLoRA additionally requires compatible CUDA/bfloat16.
Outputs use a new ignored directory. Never schedule training from CI.

Workspace experience includes LoRA/QLoRA configuration, ms-swift orchestration and
vision-language workflows; it is not a claim of measured private-model improvement.
[ms-swift reference](https://swift.readthedocs.io/en/v3.11/Instruction/Command-line-parameters.html)
is contextual, not an execution-tested dependency.

## 06 Example

Run the toy experiment, optionally --quantized-proxy. The optional_peft module defaults to a non-executing plan. Do not use --execute without separate resource and license approval.

[Example instructions](examples/README.md).

## 07 Evaluation

11 behavioral tests plus five repository-quality checks run without models,
network or GPU. Counts are regression coverage, not model-quality scores.
[Evaluation](docs/evaluation.md) · [Local validation](docs/validation.md).

## 08 Failure / Limitations

The target is deliberately easy and rank-one, not a language benchmark. Uniform 4-bit rounding is not NF4/QLoRA or a memory-saving implementation. Optional PEFT execution and dependency compatibility are unvalidated.

[Failure boundaries](docs/limitations.md).

## 09 Reproducibility

Default sample: Python 3.10+ standard library; no package install, credentials or service
required. Run from the repository root. Synthetic inputs and explicit logic support
local comparison, not reproduction of a private platform.
[Maintenance](docs/maintenance.md).

## 10 Repository Structure

- `src/`: independently written sample modules.
- `examples/`: synthetic inputs or invocation guide.
- `tests/`: behavior and repository-quality regression tests.
- `docs/`: architecture, decisions, evaluation and limitations.
- `scripts/` and `.github/`: local checks and CI configuration.

## 11 Quick Start

```sh
python3 -m src.toy_lora
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
python3 -m src.toy_lora --quantized-proxy
python3 -m src.optional_peft --mode qlora
```

CI targets Python 3.10 and 3.12. Hosted runs are pending publication.
Do not add `--execute`: actual public-model training has not been approved or validated here.

## 12 Research Relevance

Extend to licensed task datasets, pinned model revisions, held-out task metrics and resource profiling. A deliberately easy rank-one target does not establish real-data generalization.

MY CONTRIBUTION: author-confirmed engineering work. PLATFORM CONTEXT: private workflows
described conceptually. PUBLIC RECONSTRUCTION: this independent example.
FUTURE RESEARCH: unimplemented evaluation and integrations.

[Publication review](PUBLICATION.md) · [License notice](LICENSE-NOTICE.md) ·
[Security](SECURITY.md). No open-source license has been selected.
