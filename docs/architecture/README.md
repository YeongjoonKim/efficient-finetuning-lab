# Architecture evidence

2026-10-03에 코드·관리자 기능·실행 산출물과 대조한 현재 구현입니다.
각 그림의 lane은 운영 상담, 별도 Scientific Runtime, 독립 공개 예제 중 해당 범위를 표시합니다.
서로 다른 lane의 단계 사이에 자동 호출이나 배포 연결을 의미하지 않습니다.

| Diagram | Scope | Editable source |
|---|---|---|
| [Model adaptation and reproducible experiments](01_experiment_architecture.svg) | Implemented training / serving and independent public code | [Mermaid](01_experiment_architecture.mmd) |
| [Training control and adapter serving](model-serving.svg) | Implemented management workflow · observed direct-loading path | [Mermaid](model-serving.mmd) |

SVG와 Mermaid는 [동일 명세](diagrams.json)에서 생성합니다.
문구나 흐름을 수정한 뒤 `python3 scripts/render_architecture.py`로 갱신하고
`python3 scripts/render_architecture.py --check`로 동기화를 검사합니다.
그림은 일반화한 책임 구조이며 내부 주소·배포 설정·원본 코드는 포함하지 않습니다.
