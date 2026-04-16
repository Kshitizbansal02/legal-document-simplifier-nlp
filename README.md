# 🧠 AI-Powered Legal Document Simplifier

## 📌 Overview
This project is an NLP-based system that simplifies complex legal and government documents into easy-to-understand language.

---

## 🚀 Features
- Abstractive Summarization (BART)
- Paraphrasing (T5)
- Named Entity Recognition (spaCy)
- Readability Scoring
- Streamlit Web Interface

---

## ⚙️ Pipeline
Input → Summarization → Paraphrasing → NER → Readability → Output

---

## 💻 Tech Stack
- Python
- Transformers
- Streamlit
- spaCy
- textstat

---

## ▶️ How to Run

```bash
git clone https://github.com/Kshitizbansal02/legal-document-simplifier-nlp.git
cd legal-document-simplifier-nlp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
