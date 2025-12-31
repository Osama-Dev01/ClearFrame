#xlmmodel.py

from transformers import XLMRobertaForSequenceClassification, XLMRobertaTokenizer, BitsAndBytesConfig
import torch

class ModelManager:
    def __init__(self, model_name="rain12ali/tweet-classifier-xlm-roberta"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None

    def load_model(self):
        print("🔄 Loading model and tokenizer...")

        quantization_config = BitsAndBytesConfig(load_in_8bit=True) if torch.cuda.is_available() else None

        self.model = XLMRobertaForSequenceClassification.from_pretrained(
            self.model_name,
            device_map="auto" if torch.cuda.is_available() else None,
            quantization_config=quantization_config
        )

        self.tokenizer = XLMRobertaTokenizer.from_pretrained(self.model_name)

        print("✅ Model loaded successfully.")

    def predict(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=1).item()
        return predicted_class_id
