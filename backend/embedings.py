import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

df = pd.read_csv("data/cleaned_clauses.csv")

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df["clause_text"].tolist())

np.save("data/embeddings.npy", embeddings)