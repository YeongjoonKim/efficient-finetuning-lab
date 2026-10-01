# Efficient Fine-tuning Lab

### Reproducible Parameter-efficient Fine-tuning을 위한 실행 기록과 평가 경계

Dataset · Frozen Base · LoRA · Checkpoint · Evaluation · Inference

[![CI](https://github.com/YeongjoonKim/efficient-finetuning-lab/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/YeongjoonKim/efficient-finetuning-lab/actions/workflows/ci.yml)

## 실험이 남겨야 하는 것

어떤 데이터로 무엇을 학습했고, base가 실제로 고정됐는지, checkpoint로 다시 추론할 수 있는지를
확인할 수 있어야 합니다. 이 저장소는 **실제로 실행한 CPU 저랭크 실험**과
**아직 실행 검증하지 않은 공개 모델 PEFT recipe**를 분리합니다.

관리자 대시보드를 만들어 실험 성과처럼 보이게 하지 않습니다.
대신 config, split hash, frozen base hash, checkpoint와 holdout 결과를 코드·artifact로 제공합니다.

This repository is a sanitized and reconstructed technical showcase based on engineering experience from a private production AI platform.
It does not contain proprietary source code, private data, internal APIs, or production configuration.

## Experiment Architecture

![Experiment architecture](docs/architecture/01_experiment_architecture.svg)

Dataset → Preprocessing → Base Model → LoRA / QLoRA → Training
→ Checkpoint → Evaluation → Inference.

| Track | 상태 | 입증하는 것 | 입증하지 못하는 것 |
|---|---|---|---|
| CPU rank-one experiment | IMPLEMENTED | frozen base 위 adapter gradient update, holdout, 추론 | LLM/VLM 품질·실전 일반화 |
| Public-model PEFT recipe | PARTIAL | dry-run 구성과 실행 gate, LoRA/NF4 QLoRA 코드 | 의존성 호환·학습 성공·메모리 절감 |
| Task benchmark / resource profile | PROPOSED | 후속 평가 설계 | 완료된 결과가 아님 |

## 실제 Experiment Evidence

[실행 artifact](examples/execution.json)는 `python3 -m src.export_evidence`의 실제 출력입니다.
환경은 artifact에 기록되며 외부 모델이나 운영 학습 파일을 사용하지 않았습니다.

| 항목 | 기록 |
|---|---|
| Dataset | seed=19의 합성 입력; train 24 / holdout 12 |
| Experiment Config | steps=180, learning_rate=0.12, alpha=1.0 |
| Base / Adapter | frozen 16 parameters / trainable 8 parameters |
| Holdout MSE before | 0.01621627 |
| Holdout MSE after | 0.01428599 |
| Frozen base | 학습 전후 hash 동일 |
| Checkpoint format | synthetic-rank-one-v1; a, b, alpha 및 hash |
| Inference input | [0.2, -0.1, 0.4, 0.3] |

이 감소는 의도적으로 쉬운 rank-one 합성 목표에 한정됩니다.
언어모델 성능 향상이나 실작물 이미지 진단 성능으로 환산하지 않습니다.

### Checkpoint / Inference

저장된 어댑터 값을 이용한 실제 출력:

```json
[0.16199854,-0.0269989,-0.08400073,0.16199817]
```

[Exporter](src/export_evidence.py) · [학습 코드](src/toy_lora.py) ·
[Artifact 재계산 검사](tests/test_evidence.py).
환경에 따라 미세한 부동소수점 차이가 생기므로 교차 Python 버전 비교는 tolerance를 사용합니다.
snapshot 원문은 숫자 타입을 유지해 checkpoint hash와 일치시킵니다.

## LoRA / QLoRA의 구분

CPU 예제는 고정 선형 base에 저랭크 adapter만 학습합니다.
`--quantized-proxy`는 균일 4-bit 반올림 설명용이며 **NF4·double quantization·QLoRA가 아닙니다**.
packed tensor나 GPU memory saving을 구현했다고 주장하지 않습니다.

선택 PEFT 경로는 [Qwen2.5-0.5B](https://huggingface.co/Qwen/Qwen2.5-0.5B)를 후보로 합니다.
정확한 40자리 model revision, 로컬 cache, license 확인이 필요합니다.
remote code와 모델 다운로드는 비활성화되어 있습니다.
QLoRA recipe는 [공식 PEFT 안내](https://huggingface.co/docs/peft/developer_guides/quantization)에 따라
NF4 / double quantization / preparation을 구성하지만 **실제 모델 학습은 이번 공개 검증에서 실행하지 않았습니다**.

torch, transformers, peft 및 QLoRA용 bitsandbytes의 검증된 lockfile은 아직 없습니다.
QLoRA에는 별도 CUDA/bfloat16 환경 검증도 필요합니다. 기본 예제와 CI는 GPU를 사용하지 않습니다.

## Reproduce / Quick Start

Python 3.10+ 표준 라이브러리만으로 기본 실험을 실행합니다.

```sh
python3 -m src.toy_lora
python3 -m src.export_evidence
python3 -m src.toy_lora --quantized-proxy
python3 -m src.optional_peft --mode qlora
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
```

마지막 recipe는 dry-run입니다. `--execute`는 환경·모델 권리·자원 사용을 별도로 확인한 경우에만
지정해야 합니다. 운영 모델 serving을 멈추거나 training을 자동 시작하지 않습니다.

## Evaluation / Failure Analysis

19개 테스트는 loss 감소, frozen base, deterministic checkpoint, split 분리,
설정 거부, 선택형 학습 gate, 저장된 artifact와 재계산 및 저장소 검사기를 검증합니다.
seed만으로 모든 하드웨어에서 bitwise replay를 보장하지는 않습니다.

[평가 범위](docs/evaluation.md) · [설계 결정](docs/design-decisions.md) ·
[한계](docs/limitations.md) · [검증 기록](docs/validation.md).

## Repository Structure / Research Relevance

`src/`에는 CPU 실험·선택 recipe·exporter,
`examples/`에는 실제 experiment record, `tests/`에는 계약 검사,
`docs/`에는 architecture·평가·한계, `.github/`에는 CPU CI가 있습니다.

훈련 데이터·모델 lifecycle과 ms-swift 기반 구성 경험을 공개 재구성의 배경으로 설명합니다.
[ms-swift reference](https://swift.readthedocs.io/en/v3.11/Instruction/Command-line-parameters.html)는
참고 자료이지 검증된 번들 의존성이 아닙니다.

다음 연구 단계는 독립 task holdout, adapter/base/dataset revision 고정, 자원량 프로파일링,
효과 크기와 실패 사례 비교입니다. 비공개 모델 성과나 연관 없는 논문의 기여를 붙이지 않습니다.

MY CONTRIBUTION: 학습 데이터·모델 lifecycle engineering.
PLATFORM CONTEXT: 비공개 학습 workflow. PUBLIC RECONSTRUCTION: 합성 CPU 실험과 recipe.
FUTURE RESEARCH: 실제 공개 모델·독립 task 평가.

[공개 경계](PUBLICATION.md) · [License notice](LICENSE-NOTICE.md) · [Security](SECURITY.md).
