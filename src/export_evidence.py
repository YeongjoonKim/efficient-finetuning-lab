"""CPU 학습과 저장 가능한 어댑터 metadata 및 추론 예제를 실제 계산한다."""
import json
from .toy_lora import BASE, run, predict


def build():
    result = run()
    checkpoint = result["checkpoint"]
    sample = [0.2, -0.1, 0.4, 0.3]
    return {"scope": "executed_synthetic_cpu_experiment_not_llm_training",
            "experiment": result, "inference": {"input": sample,
            "output": predict(BASE, checkpoint["a"], checkpoint["b"], sample, checkpoint["alpha"])}}


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, ensure_ascii=False))
