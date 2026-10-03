# Publication Boundary — Model Adaptation & Serving

Status: PUBLICATION APPROVED for this independent evidence package.

| Layer | Repository-specific scope |
|---|---|
| Actual Engineering Experience | Qwen3.6-35B-A3B QLoRA 완료 로그, checkpoint-531, adapter 설정, vLLM 모델 목록과 학습 관리자 화면. |
| Public Reference Implementation | 선택형 PEFT LoRA/NF4 QLoRA recipe와 명시 실행 gate. optional recipe는 실제 35B run의 재현본이 아니다. |
| Public Lightweight Demo | 표준 라이브러리 CPU rank-one 업데이트, frozen base hash와 합성 train/holdout. toy 지표는 이미지 진단 정확도가 아니다. |

원천 이미지·학습 가중치·adapter·내부 model 경로·운영 설정 파일은 배포하지 않는다. 확인하지 못한 model revision과 dataset manifest hash는 unknown으로 남긴다.

회사명·직원/고객 이름·이메일·credentials는 공개하지 않는다. 승인된 화면은 원본을 보존하고
크롭/불투명 마스킹한 PNG로 관리한다. 테이블명은 사용자 승인 범위에 포함되지만 운영 데이터는 아니다.
공개 승인과 IP/NDA 적합성 및 오픈소스 license 부여는 별개의 판단이다.
[License notice](LICENSE-NOTICE.md) · [Security](SECURITY.md).

2026-10-03 추가 공개 범위: 사용자 요청에 따라 현재 관리자 기능의 조회 전용 화면과 일반화한 실행 책임 도식을 보강했습니다. 원본 코드·호스트 경로·설정·개인 데이터는 포함하지 않습니다.
