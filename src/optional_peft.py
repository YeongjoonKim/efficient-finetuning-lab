"""기본은 실행 계획 출력뿐이다. 실제 학습은 명시 옵션·캐시된 공개 모델을 요구한다."""

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re

PUBLIC_MODEL = "Qwen/Qwen2.5-0.5B"
SYNTHETIC_TEXT = tuple(f"Fictional specimen {i}: the invented index is {i + 2} points." for i in range(12))


def recipe(mode="lora", revision=None):
    if mode not in {"lora", "qlora"}:
        raise ValueError("unsupported_mode")
    if revision is not None and not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("full_revision_required")
    return {"mode": mode, "model": PUBLIC_MODEL, "revision": revision,
            "rank": 4, "alpha": 8, "learning_rate": 0.0001, "batch_size": 1, "steps": 4,
            "quantization": "bnb_nf4_double" if mode == "qlora" else "none",
            "compute": "cuda_bfloat16" if mode == "qlora" else "cpu_float32",
            "data": "new_synthetic_text", "dataset_hash": hashlib.sha256("\n".join(SYNTHETIC_TEXT).encode()).hexdigest(),
            "training_executed": False, "ready": revision is not None,
            "dependency_lock": "not_yet_validated", "download_allowed": False}


def execute(plan, *, acknowledge_license=False):
    if not acknowledge_license or not plan["ready"]:
        raise ValueError("explicit_license_ack_and_revision_required")
    # 무거운 라이브러리는 실행이 승인된 뒤에만 가져온다. 기본 dry-run은 GPU를 조회하지 않는다.
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

    quantized = plan["mode"] == "qlora"
    if quantized and (not torch.cuda.is_available() or not torch.cuda.is_bf16_supported()):
        raise RuntimeError("compatible_cuda_bf16_device_required")
    torch.manual_seed(23)
    kwargs = {"revision": plan["revision"], "local_files_only": True, "trust_remote_code": False,
              "use_safetensors": True, "torch_dtype": torch.bfloat16 if quantized else torch.float32}
    if quantized:
        kwargs.update(quantization_config=BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16), device_map={"": 0})
    tokenizer = AutoTokenizer.from_pretrained(PUBLIC_MODEL, revision=plan["revision"],
                                              local_files_only=True, trust_remote_code=False)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(PUBLIC_MODEL, **kwargs)
    if quantized:
        model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(r=plan["rank"], lora_alpha=plan["alpha"],
                                           target_modules="all-linear", task_type="CAUSAL_LM",
                                           lora_dropout=0.0, bias="none"))
    model.config.use_cache = False
    device = torch.device("cuda:0" if quantized else "cpu")
    if not quantized:
        model.to(device)
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                                 lr=plan["learning_rate"])
    model.train()
    for text in SYNTHETIC_TEXT[:plan["steps"]]:
        inputs = tokenizer(text, return_tensors="pt").to(device)
        optimizer.zero_grad()
        loss = model(**inputs, labels=inputs["input_ids"]).loss
        loss.backward()
        optimizer.step()
    model.eval()
    with torch.no_grad():
        heldout = tokenizer(list(SYNTHETIC_TEXT[8:]), padding=True, return_tensors="pt").to(device)
        labels = heldout["input_ids"].clone()
        labels[heldout["attention_mask"] == 0] = -100
        heldout_loss = float(model(**heldout, labels=labels).loss.cpu())
    # 실제 저장은 공개 예제 자신의 새 출력 폴더에 한정한다. 기존 결과를 덮어쓰지 않는다.
    output = Path("outputs") / (plan["mode"] + "-" + plan["revision"][:8])
    output.mkdir(parents=True, exist_ok=False)
    model.save_pretrained(output, safe_serialization=True)
    manifest = dict(plan, training_executed=True, heldout_loss=heldout_loss,
                    versions={n: importlib.metadata.version(n) for n in ("torch", "transformers", "peft")},
                    scope="synthetic_smoke_not_benchmark")
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("lora", "qlora"), default="lora")
    parser.add_argument("--revision")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--ack-model-license", action="store_true")
    args = parser.parse_args()
    plan = recipe(args.mode, args.revision)
    print(json.dumps(execute(plan, acknowledge_license=args.ack_model_license) if args.execute else plan, indent=2))
