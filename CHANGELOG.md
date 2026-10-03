# Changelog — Model Adaptation & Serving

## 2026-10-03 — Execution evidence and current architecture

- 관리자 실행 제어와 현재 저장된 실행·모델·배치 화면을 보강했습니다.
- 아키텍처 SVG·Mermaid를 현재 구현에 맞추고 동일 명세 기반 렌더러를 추가했습니다.
- 운영 경험·별도 Scientific 실행·독립 공개 예제의 책임과 캡처 범위를 연결했습니다.

## 2026-10-02 — Technical portfolio polish

- 기존 핵심 학습·서빙 표를 Training & Serving Facts로 통일하고 문장을 자연화했다.
- 공식 model card/config와 로컬 args·adapter·serving을 대조해 Qwen 모델 ID와 내부 architecture 이름을 설명했다.
- 530/531 step 문장의 오타를 수정하고 경량 예제 수치를 평가 문서로 옮겼다.

## 2026-10-02 — Portfolio hardening

- 학습 완료·adapter serving 근거와 공개 CPU 예제의 경계를 정리하고 재현성 항목의 확인/미확인 상태를 명시했다. 새 학습이나 모델 교체는 하지 않았다.
- 저장소별 publication, security, rights 경계를 개별화했다.
- 기존 공개 이력과 실제 화면을 유지하며 과거 개발일이나 평가 결과를 소급 생성하지 않았다.

## Existing public package

독립 예제, 회귀 검사, 비식별 실제 화면, 읽기 전용 권한의 GitHub Actions가 기존에 공개되었다.
현재 변경의 hosted CI 상태는 README의 실제 workflow 링크와 해당 PR을 기준으로 한다.
별도 release tag는 생성하지 않았다.
