"""CPU 선형 실험과 실제 모델 실행 전 보호 경계를 검사한다."""
import unittest
from src.toy_lora import Config, BASE, dataset, fingerprint, predict, quantize_proxy, run
from src.optional_peft import execute, recipe


class LabTests(unittest.TestCase):
    def test_loss_decreases_on_synthetic_holdout(self):
        result = run()
        self.assertLess(result["holdout_mse_after"], result["holdout_mse_before"])

    def test_base_is_frozen(self):
        result = run()
        self.assertEqual(result["base_hash_before"], result["base_hash_after"])
        self.assertEqual(result["trainable_parameters"], 8)

    def test_deterministic(self):
        self.assertEqual(run()["checkpoint_hash"], run()["checkpoint_hash"])

    def test_train_holdout_different(self):
        result = run()
        self.assertNotEqual(result["train_hash"], result["holdout_hash"])

    def test_checkpoint_inference(self):
        result = run()
        state = result["checkpoint"]
        self.assertEqual(fingerprint(state), result["checkpoint_hash"])
        pred = predict(BASE, state["a"], state["b"], dataset(20, 1)[0][0], state["alpha"])
        self.assertEqual(len(pred), 4)

    def test_proxy_not_claimed_qlora(self):
        result = run(Config(quantized_proxy=True))
        self.assertIn("not_qlora", result["scope"])
        self.assertNotEqual(quantize_proxy(BASE), BASE)

    def test_invalid_configs(self):
        for config in [Config(steps=True), Config(steps=0), Config(learning_rate=float("nan")),
                       Config(alpha=-1), Config(quantized_proxy=1)]:
            with self.subTest(config=config), self.assertRaises(ValueError):
                run(config)

    def test_default_recipe_never_trains(self):
        plan = recipe("qlora")
        self.assertFalse(plan["training_executed"])
        self.assertFalse(plan["ready"])
        self.assertFalse(plan["download_allowed"])

    def test_requires_real_revision_format(self):
        with self.assertRaises(ValueError):
            recipe(revision="main")

    def test_execution_gate_before_import(self):
        with self.assertRaises(ValueError):
            execute(recipe(), acknowledge_license=True)

    def test_recipe_quantization(self):
        self.assertEqual(recipe("qlora")["quantization"], "bnb_nf4_double")
        self.assertEqual(recipe()["quantization"], "none")


if __name__ == "__main__":
    unittest.main()
