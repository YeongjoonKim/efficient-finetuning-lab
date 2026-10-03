# Training Evidence Gallery

현재 학습 API가 읽는 실제 artifact를 2026-10-02 관리자 UI에서 조회했습니다.

- [실행 요약](screenshots/training-summary.png): 이력·설정·train/eval 지표.
- [학습 그래프](screenshots/training-curves.png): loss, token accuracy, gradient norm, learning rate.
- [데이터셋 drill-down](screenshots/training-label-samples.png): 정답 라벨별 수량·출처·split·샘플 이미지.
- [Checkpoint](screenshots/training-checkpoints.png): 저장된 adapter와 적용 인터페이스.

각 이미지의 목적 / 이 화면이 보여주는 것 / 아키텍처 연결은 README에서 설명합니다.
[지표 정의·완료 판정](actual-engineering.md) · [검토한 이미지 hash](screenshots/manifest.json).

## Execution management · 2026-10-03

- [실제 저장된 adapter 적용 대상](screenshots/adapter-checkpoints.png)

현재 UI를 격리된 조회 전용 브라우저에서 촬영했습니다. 모델·서비스·데이터 변경 동작은 실행하지 않았습니다.
상태·수치·실패 표시는 유지하고 공개에 불필요한 식별자를 일반화했습니다. 시간대는 Asia/Seoul입니다.
