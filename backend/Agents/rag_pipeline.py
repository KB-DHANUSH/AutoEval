from transformers import AutoTokenizer
import numpy as np
from optimum.intel.openvino import OVModelForFeatureExtraction
from sklearn.base import BaseEstimator, TransformerMixin


class SentenceSplitter(BaseEstimator, TransformerMixin):
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2', chunk_size=256, chunk_overlap=20):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def fit(self, X, y=None):
        return self

    def transform(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        chunks = []
        for text in texts:
            tokens = self.tokenizer(text, return_offsets_mapping=True, add_special_tokens=False)
            input_ids = tokens["input_ids"]
            offsets = tokens["offset_mapping"]

            start = 0
            while start < len(input_ids):
                end = min(start + self.chunk_size, len(input_ids))
                token_slice = input_ids[start:end]
                offset_slice = offsets[start:end]
                if offset_slice:
                    start_char = offset_slice[0][0]
                    end_char = offset_slice[-1][1]
                    chunk_text = text[start_char:end_char]
                    chunks.append(chunk_text)

                start += self.chunk_size - self.chunk_overlap

        return chunks

class TransformerEmbedder(BaseEstimator, TransformerMixin):
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2', device='CPU', batch_size=16):
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.ov_model = OVModelForFeatureExtraction.from_pretrained(self.model_name, export=True)

    def fit(self, X, y=None):
        # Load tokenizer and OpenVINO model
        return self

    def mean_pooling(self, hidden_states, attention_mask):
        mask = np.expand_dims(attention_mask, axis=-1).astype(np.float32)
        return np.sum(hidden_states * mask, axis=1) / np.clip(np.sum(mask, axis=1), a_min=1e-9, a_max=None)

    def transform(self, X_docs):
        all_embeddings = []
        for docs in X_docs:
            for i in range(0, len(docs), self.batch_size):
                batch = docs[i : i + self.batch_size]
                texts = [doc.page_content for doc in batch]

                enc = self.tokenizer(texts, padding=True, truncation=True, return_tensors='np')
                inputs = {k: v for k, v in enc.items()}

                outputs = self.ov_model(**inputs)
                hidden = outputs.last_hidden_state
                attn = inputs['attention_mask']  

                pooled = self.mean_pooling(hidden, attn)
                all_embeddings.append(pooled)

        return np.vstack(all_embeddings)