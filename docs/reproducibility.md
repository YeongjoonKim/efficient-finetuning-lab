# Reproducibility Inventory

2026-10-02 관측 기록에 근거하며 실제 run의 독립 재학습 재현을 주장하지 않습니다.

| Field | Actual engineering evidence | Public example |
|---|---|---|
| Model ID | Qwen/Qwen3.6-35B-A3B, local card/args/serving 교차 확인 | CPU synthetic base; optional Qwen2.5-0.5B recipe는 별개 |
| Model revision/hash | Immutable upstream revision 및 전체 weight hash 미확인 | optional 실행은 명시 revision gate 필요 |
| Architecture ID | Qwen3_5MoeForConditionalGeneration: 내부 transformers 식별자 | actual model 명칭과 혼동하지 않음 |
| Training config | 3 epochs, LR 0.0001, batch 1, accumulation 16, max length 2048 | toy config와 artifacts는 공개 코드로 재계산 |
| Adapter | rank 16, alpha 32, all-linear, frozen vision encoder | CPU rank-one; 실제 LoRA/NF4와 구분 |
| Dataset manifest | 현재 train 2,822 / val 135; 완료 run의 immutable manifest hash 미확인 | 합성 train 24 / holdout 12 |
| Checkpoint | checkpoint-531 완료 상태·파일 확인; 파일 hash는 공개하지 않음 | toy checkpoint hash와 frozen-base 검증 |
| Serving config | vLLM TP 4, bfloat16, context 40,960, adapter rank 16 | 실제 serving 없음; CPU 예제와 optional training gate |

현재 dataset 조회값은 완료 run의 불변 데이터 snapshot을 대체하지 않습니다.
토큰 정확도는 이미지 진단 정확도가 아니며 독립 holdout 평가가 남아 있습니다.
향후 확보할 것은 승인 가능한 model revision, 완료 run manifest와 split hash, 환경 lock,
자원 측정 및 독립 품질 평가입니다. 확인하지 않은 식별자를 생성하지 않습니다.

[Actual evidence](actual-engineering.md) · [Evaluation](evaluation.md).
