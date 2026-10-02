# Efficient Fine-tuning Lab

### Qwen 35B QLoRA · Dataset Curation · Experiment Management · vLLM Serving

[![CI](https://github.com/YeongjoonKim/efficient-finetuning-lab/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/YeongjoonKim/efficient-finetuning-lab/actions/workflows/ci.yml)

## 실제 구현 경험

이 프로젝트는 **Model adaptation → Experiment tracking → Serving**을 다룹니다.
35B QLoRA 학습·서빙 파이프라인과 경량 공개 재현 예제를 구분해 제공합니다.

농업 이미지와 한국어 정답 라벨을 연결하는 데이터셋, **Qwen3.6-35B-A3B의 QLoRA 학습**,
학습 이력·지표·체크포인트 관리, vLLM adapter serving을 구현했습니다.

## Training & Serving Facts

| 항목 | 구성 및 구현 |
|---|---|
| Base Model | **Qwen/Qwen3.6-35B-A3B** — 총 35B, 활성 3B MoE |
| Training | ms-swift · bitsandbytes **4-bit NF4 + double quantization** · bfloat16 compute |
| Adapter | LoRA rank 16 / alpha 32 · all-linear · vision encoder frozen |
| Completed Run | 3 epochs · **531 / 531 steps** · checkpoint-531 |
| Evaluation | loss **0.19017857**, token accuracy **0.95468998** |
| Serving | vLLM · tensor parallel 4 · checkpoint-531 직접 adapter loading |

Token accuracy는 정답 시퀀스의 토큰 단위 지표이며 진단 정확도와 구분합니다.
[상세 근거와 지표 정의](docs/actual-engineering.md).

## 학습·서빙 아키텍처

![데이터셋부터 QLoRA 학습과 vLLM 서빙까지](docs/architecture/model-serving.svg)

공공 이미지 / 검수된 수집분 → 클래스별 데이터셋 → QLoRA → 지표·checkpoint
→ adapter loading → vLLM → 이미지 모델을 사용하는 애플리케이션.

학습 관리 서비스에 데이터셋 재구성·작업 상태 관리·모델 적용 경로를 연결했습니다.
현재 serving은 **checkpoint-531 직접 adapter loading**입니다.
merge 후 적용 경로도 구현되어 있으며 현재 사용 경로와 구분해 설명합니다.

## 학습 모니터링

**목적** — 실행별 설정과 진행 상태를 같은 화면에서 확인합니다.

![학습 실행 이력과 요약](docs/screenshots/training-summary.png)

**이 화면이 보여주는 것** — 실행 이력, train/eval 지표, hyperparameter 조회가 학습 산출물에 연결됩니다.
화면의 마지막 training log는 530 step을 표시하지만, trainer state에서는 531 step 완료를 확인할 수 있습니다.
**아키텍처 연결** — Training → Experiment Tracking.

### 학습 곡선

**목적** — loss·token accuracy·gradient norm·learning rate로 학습 진행을 관찰합니다.

![Loss와 token accuracy 등 학습 곡선](docs/screenshots/training-curves.png)

**이 화면이 보여주는 것** — 저장된 train/eval 로그의 네 가지 그래프.
**아키텍처 연결** — Training → Monitoring → Checkpoint Selection.

## 데이터 수집과 큐레이션

공공 병해충 이미지·온실 이미지·관리자 업로드·외부 수집 staging 데이터를 공통 학습 형식으로 연결했습니다.
외부 수집분은 중복 검사와 라벨 검수·승인 후 다음 데이터셋 build에 반영됩니다.

캡처 시점 활성 데이터셋은 **train 2,822 / validation 135 / 855 labels**입니다.
외부 수집분 **4,520장은 다음 빌드 대기**이며 완료된 학습의 사용량에 더하지 않습니다.

**목적** — 정답 라벨별 수량과 이미지를 함께 보며 불균형·라벨 오류를 검토합니다.

![라벨별 수량과 학습 이미지 샘플](docs/screenshots/training-label-samples.png)

**이 화면이 보여주는 것** — 클래스 검색, 소스 필터, 선택 라벨의 이미지·split drill-down.
**아키텍처 연결** — Acquisition → Curation → Dataset.

## 체크포인트 관리

**목적** — 저장된 adapter를 실행 이력과 연결해 선택합니다.

![저장된 adapter와 체크포인트 관리](docs/screenshots/training-checkpoints.png)

**이 화면이 보여주는 것** — checkpoint-400 / 500 / 531과 모델 적용 인터페이스.
**아키텍처 연결** — Training Artifact → Deployment Decision → Serving.

## 시스템 설계의 강점

| 설계 | 구현 효과 |
|---|---|
| Dataset visibility | 정답 라벨·출처·split·이미지를 한 흐름에서 검토 |
| Experiment traceability | args, step별 로그, trainer state, adapter를 실행 단위로 연결 |
| Parameter-efficient training | quantized base와 학습 가능한 adapter의 역할 분리 |
| Adapter lifecycle | 학습 완료와 실제 serving model 목록을 각각 확인 |

## 공개 구현 범위

| 구분 | 공개 범위 |
|---|---|
| 운영 시스템 | Qwen 35B QLoRA 학습·관리 UI·adapter serving |
| Public Reference Implementation | 선택형 PEFT LoRA / NF4 QLoRA recipe와 실행 gate |
| Public Lightweight Demo | CPU rank-one 실험, frozen base hash, checkpoint, holdout |

![Public experiment reference architecture](docs/architecture/01_experiment_architecture.svg)

CPU 예제는 합성 데이터로 adapter 업데이트와 frozen base, checkpoint 재현을 확인합니다.
[실행 artifact](examples/execution.json)의 상세 수치는 [평가 문서](docs/evaluation.md)에 정리했습니다.
선택형 recipe의 Qwen2.5-0.5B는 **공개 재현용 후보**이며 실제 35B 학습 모델과 별개입니다.

## 실행 및 검증

Python 3.10+ 표준 라이브러리로 기본 예제를 실행합니다.

```sh
python3 -m src.toy_lora
python3 -m src.export_evidence
python3 -m src.optional_peft --mode qlora
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
```

선택형 PEFT 명령은 기본 dry-run입니다. 실제 실행에는 고정 revision·로컬 cache·의존성·사용권·GPU 확인이 필요합니다.
공개 테스트는 frozen base, checkpoint, split, 실행 gate와 artifact 재계산을 검증합니다.

## 현재 범위와 한계

CPU 예제는 LoRA 동작을 빠르게 확인하기 위한 경량 샘플이며, 35B QLoRA는 NF4 + double quantization으로 구성됩니다.
데이터셋 화면은 활성 build 기준으로, 완료 run의 불변 manifest 고정은 [재현성 과제](docs/reproducibility.md)로 관리합니다.
독립 이미지 holdout, 희소 클래스의 검증 coverage, 모델 revision 고정과 자원 프로파일 비교가 다음 평가 항목입니다.
공개 범위는 학습·서빙의 설계 근거와 재현 예제이며 운영 가중치·원천 데이터는 별도로 관리합니다.

[상세 근거](docs/actual-engineering.md) · [평가](docs/evaluation.md) ·
[검증 기록](docs/validation.md) · [공개 경계](PUBLICATION.md) ·
[License notice](LICENSE-NOTICE.md) · [Security](SECURITY.md).
