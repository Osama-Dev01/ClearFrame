# factualmodel.py
from transformers import XLMRobertaForSequenceClassification, XLMRobertaTokenizer, BitsAndBytesConfig
import torch

class FactualityClassifier:
    def __init__(self, model_name="rain12ali/factual_nonfactual-classifier-xlm-roberta"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None

        # ✅ FIXED: Swapped labels to match model output behavior
        self.label_map = {
            0: "Factual",
            1: "Non-Factual"
        }

    def load_model(self):
        """Load the model and tokenizer with optional quantization"""
        print("🔄 Loading factuality classification model...")

        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_threshold=6.0
        ) if torch.cuda.is_available() else None

        self.model = XLMRobertaForSequenceClassification.from_pretrained(
            self.model_name,
            device_map="auto" if torch.cuda.is_available() else None,
            quantization_config=quantization_config,
            num_labels=2
        )

        self.tokenizer = XLMRobertaTokenizer.from_pretrained(
            self.model_name,
            model_max_length=512
        )

        print("✅ Factuality classifier loaded successfully.")

    def predict(self, text: str, return_probs: bool = False):
        """Classify text as factual or non-factual"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        if torch.cuda.is_available():
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        logits = outputs.logits
        probs = torch.softmax(logits, dim=1)
        predicted_class_id = torch.argmax(probs, dim=1).item()

        result = {
            "prediction": self.label_map[predicted_class_id],
            "class_id": predicted_class_id
        }

        if return_probs:
            result["probabilities"] = {
                "Factual": probs[0][0].item(),
                "Non-Factual": probs[0][1].item()
            }

        return result

    def batch_predict(self, texts: list, batch_size: int = 8):
        """Classify multiple texts in batches"""
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512
            )

            if torch.cuda.is_available():
                inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)

            batch_probs = torch.softmax(outputs.logits, dim=1)
            batch_preds = torch.argmax(batch_probs, dim=1)

            for j, pred in enumerate(batch_preds):
                results.append({
                    "text": batch[j],
                    "prediction": self.label_map[pred.item()],
                    "class_id": pred.item(),
                    "probability": batch_probs[j][pred].item()
                })

        return results
