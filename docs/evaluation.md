# Evaluation

19개 테스트가 합성 holdout loss, frozen base, checkpoint, split, 설정과 실행 gate, 저장한 artifact 및 저장소 검사기를 확인합니다. Python별 미세한 산술 차이는 tolerance로 비교하며 저장본 checkpoint 자체의 hash도 검사합니다.

후속 연구는 독립적인 task label과 baseline을 분리해야 합니다. 합성 회귀 통과율을 현장 성능으로 해석하지 않습니다.
