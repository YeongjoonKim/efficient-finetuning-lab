"""외부 패키지·GPU 없이 저랭크 어댑터만 학습하는 합성 선형 실험이다."""

import argparse
import hashlib
import json
import math
import platform
import random
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Config:
    seed: int = 19
    steps: int = 180
    learning_rate: float = 0.12
    alpha: float = 1.0
    quantized_proxy: bool = False

    def validate(self):
        if type(self.seed) is not int or type(self.steps) is not int or not 1 <= self.steps <= 2000:
            raise ValueError("invalid_steps_or_seed")
        if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 < v <= 1
               for v in (self.learning_rate, self.alpha)):
            raise ValueError("invalid_hyperparameter")
        if type(self.quantized_proxy) is not bool:
            raise ValueError("invalid_quantization")


BASE = ((0.31, -0.12, 0.07, 0.2), (-0.1, 0.42, 0.11, -0.03),
        (0.08, 0.15, -0.28, 0.09), (0.17, -0.08, 0.03, 0.36))
LEFT = (0.4, -0.3, 0.2, 0.5)
RIGHT = (0.3, 0.1, -0.4, 0.2)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def dataset(seed, count):
    rng = random.Random(seed)
    result = []
    for _ in range(count):
        x = [rng.uniform(-1, 1) for _ in range(4)]
        y = [sum((BASE[i][j] + LEFT[i] * RIGHT[j]) * x[j] for j in range(4))
             for i in range(4)]
        result.append((x, y))
    return result


def quantize_proxy(matrix):
    """단순 균일 4비트 근사이며 NF4·이중 양자화·QLoRA 구현이 아니다."""
    scale = max(abs(v) for row in matrix for v in row) / 7
    return tuple(tuple(round(v / scale) * scale for v in row) for row in matrix)


def predict(base, a, b, x, alpha=1.0):
    projection = sum(a[j] * x[j] for j in range(4))
    return [sum(base[i][j] * x[j] for j in range(4)) + alpha * b[i] * projection
            for i in range(4)]


def mse(base, a, b, rows, alpha=1.0):
    return sum(sum((p - t) ** 2 for p, t in zip(predict(base, a, b, x, alpha), y))
               for x, y in rows) / (len(rows) * 4)


def run(config=Config()):
    config.validate()
    train, holdout = dataset(config.seed, 24), dataset(config.seed + 1, 12)
    base = quantize_proxy(BASE) if config.quantized_proxy else BASE
    before_hash = fingerprint(base)
    rng = random.Random(config.seed + 2)
    a, b = [rng.uniform(-0.2, 0.2) for _ in range(4)], [0.0] * 4
    baseline = mse(base, a, b, holdout, config.alpha)
    for _ in range(config.steps):
        grad_a, grad_b = [0.0] * 4, [0.0] * 4
        for x, target in train:
            error = [p - t for p, t in zip(predict(base, a, b, x, config.alpha), target)]
            dot = sum(a[j] * x[j] for j in range(4))
            for j in range(4):
                grad_a[j] += 2 * config.alpha * sum(error[i] * b[i] for i in range(4)) * x[j] / (len(train) * 4)
            for i in range(4):
                grad_b[i] += 2 * config.alpha * error[i] * dot / (len(train) * 4)
        a = [v - config.learning_rate * g for v, g in zip(a, grad_a)]
        b = [v - config.learning_rate * g for v, g in zip(b, grad_b)]
    checkpoint = {"format": "synthetic-rank-one-v1", "a": a, "b": b, "alpha": config.alpha}
    return {"disclosure": "Reconstructed Public Experiment",
            "scope": "linear_rank_one_not_llm_not_qlora", "config": asdict(config),
            "base_hash_before": before_hash, "base_hash_after": fingerprint(base),
            "train_hash": fingerprint(train), "holdout_hash": fingerprint(holdout),
            "base_parameters": 16, "trainable_parameters": 8,
            "holdout_mse_before": baseline, "holdout_mse_after": mse(base, a, b, holdout, config.alpha),
            "checkpoint": checkpoint, "checkpoint_hash": fingerprint(checkpoint),
            "environment": {"python": platform.python_version(), "dependencies": "stdlib"},
            "limitations": ["Synthetic regression only", "No language or vision quality measured",
                            "4-bit proxy is not NF4 and does not measure memory savings"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quantized-proxy", action="store_true")
    options = parser.parse_args()
    print(json.dumps(run(Config(quantized_proxy=options.quantized_proxy)), indent=2))
