# Scope & Limitations

실제 Qwen 35B NF4 QLoRA 완료와 vLLM adapter 등록은 [artifact와 runtime](actual-engineering.md)에서 확인했습니다. token accuracy는 이미지 진단 정확도와 구분합니다.

공개 CPU 예제는 합성 rank-one 학습이고 uniform 4-bit proxy는 설명용입니다. 별도 공개 PEFT recipe는 dependency lock과 실제 실행 검증이 남아 있습니다. 현재 데이터셋 조회값과 완료 run의 불변 snapshot도 구분합니다.
