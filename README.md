# ⚖️ AI-Powered Legal Document Simplifier

> A privacy-preserving NLP pipeline that transforms complex legal clauses into plain English — grounded in 13,000+ real lawyer-labeled contracts.

---

## 📌 Overview

Most people — freelancers, small business owners, students — sign contracts without fully understanding what they're agreeing to. Hiring a lawyer for every clause is expensive and slow.

This system reads any legal clause and instantly tells you:
- **What it means** in plain English
- **How risky it is** with a confidence score
- **What similar clauses** look like in real contracts

Built as an NLP mini-project using a six-stage pipeline: OCR/file extraction → input validation → anonymization → embedding → risk classification → LLM explanation → semantic retrieval.

---

## 🤔 How Is This Different From ChatGPT?

| Feature | This System | ChatGPT |
|---|---|---|
| Privacy | Anonymizes entities before any LLM call | Sends raw text to external API |
| Grounding | Retrieves real clauses from 13,000+ labeled contracts | Generates from training data |
| Risk Score | Trained classifier with confidence % | Generic opinion |
| Similar Clauses | Cosine similarity over real SEC-filed contracts | None |
| File Input | PDF + scanned images via OCR | Text only |
| Input Validation | Rejects non-legal content before pipeline | No filtering |
| Architecture | 6-stage NLP pipeline | Single prompt |

---

## 🧠 NLP Techniques Used

| Technique | Tool | Purpose |
|---|---|---|
| Named Entity Recognition | spaCy `en_core_web_sm` | Identify and anonymize persons, orgs, dates, money |
| Sentence Embeddings | `all-MiniLM-L6-v2` (Sentence-BERT) | Convert clauses to 384-dim semantic vectors |
| Cosine Similarity Search | scikit-learn | Retrieve most similar real clauses from database |
| Text Classification | Logistic Regression on embeddings | Predict risk level (low / medium / high) with confidence |
| Abstractive Generation | LLaMA 3.1 via Groq | Generate plain-English simplification |
| OCR | Tesseract v5 + PyMuPDF | Extract text from scanned PDFs and images |
| Input Validation | Keyword heuristics + regex | Reject non-legal content before pipeline |

---

## ⚙️ System Architecture

```
Input (Text / PDF / Image)
       │
       ▼
[ File Extractor ]       PyMuPDF → digital PDF text extraction
       │                 Tesseract OCR → scanned PDFs & images
       │                 Smart fallback: digital first, OCR if sparse
       │
       ▼
[ Input Validator ]      3-stage check:
       │                 1. Length & sanity (min 20 chars, min 5 words)
       │                 2. Instant-reject (greetings, code, SQL, emoji)
       │                 3. Legal keyword check (80-word legal vocabulary)
       │                 → Rejects non-legal content with clear error message
       │
       ▼
[ Anonymizer ]           spaCy NER → replace PERSON, ORG, DATE, MONEY
       │                 with placeholders → privacy preserved
       │
       ├──────────────► [ Risk Classifier ]
       │                 MiniLM embedding → LogisticRegression
       │                 → level + confidence score
       │
       ├──────────────► [ LLM — Groq/LLaMA 3.1 ]
       │                 Single structured call on anonymized text
       │                 → simplified + risk_explanation (JSON)
       │
       └──────────────► [ Similarity Search ]
                         Cosine similarity over CUAD clause embeddings
                         → top-5 real similar clauses with scores
       │
       ▼
[ Deanonymizer ]         Restore original entity names in LLM output
       │
       ▼
[ API Response ]
```

---

## 📊 Dataset

The clause database and risk classifier are trained on the **CUAD (Contract Understanding Atticus Dataset)**:
- 510 real commercial contracts from SEC EDGAR filings
- 13,101 clauses labeled by law students, reviewed by experienced lawyers
- 41 clause types including Anti-Assignment, Exclusivity, Governing Law, Termination
- Licensed under CC BY 4.0

> Source: Hendrycks et al., NeurIPS 2021 — [arxiv.org/abs/2103.06268](https://arxiv.org/abs/2103.06268)

---

## 🚀 Features

- 🔒 **Privacy-Preserving** — entities anonymized before any external API call
- 📄 **Multi-Format Input** — accepts PDF (digital + scanned) and images (PNG, JPG, TIFF, BMP)
- 🔍 **OCR Support** — Tesseract v5 extracts text from scanned documents automatically
- 🛡️ **Input Validation** — rejects non-legal content before hitting the NLP pipeline
- 📊 **Risk Classification** — trained classifier returns `low / medium / high` + confidence %
- 🔍 **Semantic Retrieval** — finds real similar clauses from 13,000+ labeled examples
- 💬 **Plain English Output** — LLM explains the clause in language a non-lawyer can understand
- ✅ **55 Tested Cases** — full pytest suite covering unit + integration + edge cases
- 🌐 **React Frontend** — modern dark-theme UI with drag-and-drop file upload

---

## 💻 Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| NER | spaCy `en_core_web_sm` |
| Embeddings | Sentence-Transformers `all-MiniLM-L6-v2` |
| Classifier | scikit-learn LogisticRegression |
| LLM | LLaMA 3.1 8B via Groq API |
| OCR | Tesseract v5 + PyMuPDF + Pillow |
| Input Validation | Custom heuristic validator |
| Frontend | React + Next.js (v0) |
| Testing | pytest + FastAPI TestClient |

---

## ▶️ Setup

### Prerequisites

- Python 3.13+
- Node.js 18+
- A free [Groq API key](https://console.groq.com)

---

### 1. Clone the repository

```bash
git clone https://github.com/Kshitizbansal02/legal-document-simplifier-nlp.git
cd legal-document-simplifier-nlp
```

---

### 2. Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install Python dependencies
pip install -r requirements.txt

# If PyMuPDF fails on Python 3.13 (no pre-built wheel for 1.24.5):
pip install PyMuPDF==1.24.11

# If FastAPI raises a python-multipart error:
pip install "python-multipart>=0.0.13"

# Download spaCy language model
python -m spacy download en_core_web_sm
```

---

### 3. Install Tesseract OCR

Tesseract must be installed at the OS level — it is not a Python package.

**Windows:**
1. Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install it (default path: `C:\Program Files\Tesseract-OCR\`)
3. Open `services/file_extractor.py` and set:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

Verify:
```bash
tesseract --version   # should print: tesseract v5.x.x
```

---

### 4. Configure environment variables

Create `backend/.env` and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

---

### 5. Train the risk classifier

> ⚠️ Required. The backend will fail to start if `models/risk_clf.pkl` does not exist.

```bash
# From backend/ folder
python scripts/Train_risk.py
```

Run once — no need to retrain unless the dataset changes.

---

### 6. Configure pytest (required for tests)

Create `backend/pytest.ini`:
```ini
[pytest]
pythonpath = .
```

---

### 7. Start the backend

```bash
# From backend/ folder
uvicorn main:app --reload
```

- **API:** `http://localhost:8000`
- **Swagger docs:** `http://localhost:8000/docs`

Wait for `INFO: Application startup complete.` before making requests.

---

### 8. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local

# Start the dev server
npm run dev
```

Frontend runs at `http://localhost:3000` (or `3001` if 3000 is in use).

> Make sure the backend is running before using the frontend.

---

### 9. Verify everything works

```bash
# From backend/ folder — create and test a sample PDF
python -c "
import fitz, requests
doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 72), 'The Licensee shall not assign or sublicense any rights without prior written consent.')
doc.save('test_clause.pdf')
with open('test_clause.pdf', 'rb') as f:
    r = requests.post('http://localhost:8000/api/v1/upload', files={'file': ('test_clause.pdf', f, 'application/pdf')})
    print(r.status_code)   # 200
    print(r.json()['risk']['level'])  # low / medium / high
"
```

---

## 🧪 Running Tests

```bash
# From backend/ folder
python -m pytest tests/ -v
```

55 tests across 8 categories:
- `TestHealth` — API startup and model loading
- `TestAnonymizer` — NER entity detection and restoration
- `TestSimilarity` — embedding search and score ordering
- `TestRiskPrediction` — classifier output validation
- `TestAnalyzeEndpoint` — full pipeline integration
- `TestFileExtractor` — OCR and PDF extraction
- `TestUploadEndpoint` — file upload endpoint integration
- `TestEdgeCases` — empty input, long input, mixed language

---

## 📡 API Reference

### `POST /api/v1/analyze`

**Request:**
```json
{ "text": "The Licensee shall not assign or sublicense any rights without prior written consent." }
```

**Response:**
```json
{
  "anonymized_text": "The [PERSON_1] shall not assign...",
  "simplified": "You cannot give away your rights without getting permission first.",
  "risk_explanation": "This limits your flexibility and could trap you in the agreement.",
  "risk": {
    "level": "high",
    "confidence": 0.827,
    "description": "Significant legal or financial risk. Legal counsel strongly advised.",
    "method": "classifier"
  },
  "similar_clauses": [
    {
      "clause_text": "Licensee may not assign this Agreement...",
      "clause_type": "Anti-Assignment",
      "risk_level": "high",
      "score": 0.746
    }
  ]
}
```

### `POST /api/v1/upload`

**Request:** `multipart/form-data` with a `file` field

**Supported formats:** `.pdf`, `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.webp`

**Max file size:** 10 MB

**Response:** Same as `/analyze` plus:
```json
{
  "extraction_meta": {
    "filename": "contract.pdf",
    "file_type": ".pdf",
    "characters_extracted": 1024,
    "extraction_method": "digital"
  }
}
```

**Error codes:**

| Code | Meaning |
|---|---|
| 400 | Empty file |
| 413 | File exceeds 10 MB |
| 415 | Unsupported file type |
| 422 | Non-legal content detected or insufficient text extracted |
| 503 | Models still loading — retry in a few seconds |

---

## 🛡️ Input Validation

All input is validated before entering the NLP pipeline:

| Check | Rule |
|---|---|
| Length | Minimum 20 characters, maximum 50,000 |
| Word count | Minimum 5 words |
| Pattern rejection | Blocks greetings, code snippets, SQL queries, emoji-only input |
| Legal keyword check | Requires at least 1 legal term from an 80-word vocabulary |

Non-legal content returns a `422` error with a descriptive message.

---

## ⚠️ Limitations

- spaCy occasionally misclassifies legal role words (e.g. "Licensee") as persons — known limitation of general-purpose NER on legal text
- Risk classifier performance depends on CUAD label distribution — uncommon clause types may have lower accuracy
- LLM responses are non-deterministic; system uses `temperature=0.2` for consistency
- OCR accuracy depends on scan quality — very low resolution or handwritten documents may not extract well
- PyMuPDF `1.24.5` has no pre-built wheel for Python 3.13 on Windows — use `1.24.11+`

---

## 🔮 Future Improvements

- 🌍 Multi-language support (Hindi, Tamil)
- 🔊 Voice-based clause explanation
- ☁️ Cloud deployment
- 🤖 Fine-tuned legal-specific embedding model (legal-bert)
- 💬 Q&A mode — ask questions about an uploaded document
- 📊 Analytics dashboard

---

## 👨‍💻 Author

**Vansh C** — B.Tech CSE (AIML)

---

## 📜 License

This project is for academic and educational purposes. Dataset (CUAD) is licensed under CC BY 4.0.