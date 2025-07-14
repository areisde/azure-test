import os
import numpy as np
from huggingface_hub import InferenceClient
from sklearn.preprocessing import normalize 

model = InferenceClient(
    provider="hf-inference",
    api_key=os.environ.get("HF_TOKEN"),
    model="sentence-transformers/all-MiniLM-L6-v2"
)

def embed_text(text):
    # Embed text
    vec = model.feature_extraction(text)

    # Convert to numpy array
    embedding_np = np.array(vec)

    # Normalize manually (L2)
    embedding_norm = normalize(embedding_np.reshape(1, -1), norm="l2")[0]
    return embedding_norm





