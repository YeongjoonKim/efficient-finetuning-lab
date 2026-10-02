# Actual Training & Serving Evidence

검토일: 2026-10-02. 원본 설정·학습 로그·파일 존재·현재 runtime·관리자 UI를 교차 확인했습니다.
이 문서는 공개 가능한 관측 기록이며 비공개 학습 파일 자체는 배포하지 않습니다.

| Claim | 확인한 근거 | 판정 |
|---|---|---|
| Qwen3.6-35B-A3B | 로컬 model card, 학습 args의 모델 경로, serving model mount | 실제 base model 확인 |
| QLoRA | args의 bnb / 4 bits / nf4 / double quantization / bfloat16 | 실제 quantized training 확인 |
| Adapter 구성 | args와 adapter_config의 rank 16, alpha 32, all-linear | 실제 adapter 설정 확인 |
| 학습 완료 | trainer_state의 epoch 3, global_step=max_steps=531 | 완료 |
| Checkpoints | 400 / 500 / 531의 adapter 파일과 trainer state | 파일 존재 확인 |
| Serving | vLLM 실행 인자와 model mount, 모델 목록의 adapter-parent 관계 | 현재 base와 adapter 등록 확인 |
| 관리자 모니터링 | 학습 API가 args / logging / dataset을 읽고 UI에서 표시 | 실제 데이터 연동 |

## Configuration

실행 ID: v0-20260724-144112. ms-swift SFT, batch size 1, gradient accumulation 16,
learning rate 0.0001, max length 2048, epochs 3. Vision encoder를 고정하고 language-side adapter를 학습합니다.
모델의 transformers architecture 식별자는 Qwen3_5MoeForConditionalGeneration입니다.
이는 로컬 Qwen3.6 model card 및 학습 경로와 함께 확인한 호환 architecture 명칭입니다.

학습 스크립트는 4개 GPU에 단일 프로세스 device_map auto로 배치합니다.
이를 DDP 학습으로 표현하지 않습니다. YOLO의 DDP 학습과도 별도입니다.

## Completion & Evaluation

최종 로그: train runtime 20,362.4431초, aggregate train loss 0.41021487,
eval loss 0.19017857, eval token accuracy 0.95468998.

관리자 progress는 마지막 train log인 530 / 531을 표시하지만 최종 eval과 trainer state는 531입니다.
학습 완료 판정은 UI의 반올림 100%가 아니라 완료 artifact를 기준으로 했습니다.
학습 이력의 약 2,832장 표시는 step 기반 추정이고 현재 dataset API의 실제 train count는 2,822장입니다.

## Dataset Management

현재 dataset API: NCPMS 2,327 + 온실 630 = 2,957장, train 2,822 / val 135, 855 labels.
클래스별 분할기는 4장 미만 클래스를 train에만 배치하므로 모든 클래스가 validation에 포함되지는 않습니다.
이 조회값은 현재 파일 기준이며 완료 run에 고정된 manifest hash를 대신하지 않습니다.

외부 수집 → staging → 중복/라이선스·라벨 검토 → 승인 → committed manifest → 다음 build 경로가 연결되어 있습니다.
API와 build 함수를 대조했으며 현재 4,520장은 다음 build 대기입니다.
라이선스 정책에는 관리자 override가 존재하므로 자동 필터를 권리 확인의 보증으로 표현하지 않습니다.

## Serving Lifecycle

현재 vLLM: tensor parallel 4, bfloat16, context limit 40,960, prefix caching,
LoRA enabled, maximum rank 16. checkpoint-531 adapter가 모델 목록에 base의 자식으로 나타납니다.
모델 목록 조회는 로딩 확인이며 새로운 생성 요청의 품질·latency benchmark는 아닙니다.

학습 watcher의 merge/export·적용·실패 시 복구 경로와 현재 direct adapter loading을 구분했습니다.
이번 검토는 학습 시작·중지·merge·모델 교체·컨테이너 재시작을 수행하지 않았습니다.

## Evidence Screens

[학습 요약](screenshots/training-summary.png) · [학습 곡선](screenshots/training-curves.png) ·
[라벨·이미지](screenshots/training-label-samples.png) · [체크포인트](screenshots/training-checkpoints.png).

현재 UI를 1920×1080 브라우저로 읽기 전용 캡처하고 필요한 영역만 크롭했습니다.
개인 계정으로 로그인하거나 운영 인증을 변경하지 않고 격리된 검증 identity로 읽기 전용 API를 호출했습니다.
