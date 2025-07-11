from sentence_transformers import SentenceTransformer

model = SentenceTransformer('intfloat/e5-large-v2')

def embed_text(text):
    return model.encode(text)
