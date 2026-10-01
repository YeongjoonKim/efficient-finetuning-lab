# Design Decisions

실행한 CPU low-rank 학습과 실행하지 않은 PEFT recipe를 분리합니다. base를 고정하고 train/holdout과 checkpoint를 기록합니다. 선택형 학습은 revision·license·로컬 모델 cache 확인을 요구합니다.
