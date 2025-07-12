from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2',
                            revision="main",
                            trust_remote_code=False)

def embed_text(text):
    vec = model.encode([text],
                        normalize_embeddings=True,
                        convert_to_numpy=True,
                        )
    return vec[0]
