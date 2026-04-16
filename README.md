🧠 AI-Powered Legal Document Simplifier (Legal NLP)


⸻

📌 Overview

Understanding legal and government documents is challenging due to their complex language and structure.
This project presents an AI-powered NLP system that transforms such documents into simple, readable, and user-friendly explanations.

The system leverages state-of-the-art transformer models along with linguistic processing techniques to ensure semantic accuracy and improved readability.

⸻

🎯 Problem Statement

Legal and policy documents:
	•	Are written in complex legal language
	•	Are difficult for common users to interpret
	•	Lead to misunderstanding and low accessibility

👉 There is a clear gap between legal information and public understanding.

⸻

💡 Proposed Solution

We developed a system that:
	•	Simplifies complex legal text
	•	Preserves original meaning
	•	Improves readability score
	•	Extracts key entities

👉 The system bridges the gap between technical legal language and common users.

⸻

⚙️ System Architecture

Input Legal Text
        ↓
Text Preprocessing
        ↓
Abstractive Summarization (BART)
        ↓
Paraphrasing (T5 Transformer)
        ↓
Named Entity Recognition (spaCy)
        ↓
Readability Scoring (Flesch Reading Ease)
        ↓
Final Simplified Output


⸻

🚀 Features
	•	🔍 Abstractive Summarization
	•	Uses transformer models to condense long legal text
	•	✏️ Paraphrasing Engine
	•	Converts formal/legal language into simpler sentences
	•	🧾 Named Entity Recognition (NER)
	•	Extracts key entities like laws, sections, and dates
	•	📊 Readability Analysis
	•	Measures improvement using Flesch Reading Ease score
	•	🌐 Interactive Web Interface
	•	Built with Streamlit for real-time usage
	•	⚡ End-to-End NLP Pipeline
	•	Fully automated processing from input to output

⸻

🧠 NLP Techniques Used

Technique	Purpose
Transformers (BART, T5)	Context-aware summarization & paraphrasing
Tokenization	Text preprocessing
Named Entity Recognition	Extract important entities
Readability Metrics	Evaluate simplification quality


⸻

💻 Tech Stack
	•	Language: Python
	•	Libraries: HuggingFace Transformers, spaCy, textstat
	•	Frontend: Streamlit
	•	ML Models: BART, T5

⸻

▶️ Installation & Setup

# Clone the repository
git clone https://github.com/Kshitizbansal02/legal-document-simplifier-nlp.git

# Navigate to project folder
cd legal-document-simplifier-nlp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run the application
streamlit run app.py


⸻

📈 Example

🔹 Input:

“The applicant shall be eligible subject to compliance with clause 4.2 of the policy…”

🔹 Output:

“You can apply if you meet the conditions mentioned in section 4.2.”

🔹 Improvement:
	•	Readability Score: Low → High
	•	Complexity: Reduced

⸻

🎯 Impact
	•	Enhances accessibility of legal documents
	•	Reduces misinterpretation of policies
	•	Helps non-experts understand legal information
	•	Useful for government, education, and public services

⸻

⚠️ Limitations
	•	May slightly simplify legal precision
	•	Depends on pretrained model accuracy
	•	Requires computational resources

⸻

🔮 Future Improvements
	•	🌍 Multi-language support
	•	🔊 Voice-based explanation
	•	☁️ Cloud deployment (public access)
	•	📊 Dashboard for analytics
	•	🤖 Fine-tuned legal-specific models

⸻

👨‍💻 Author

Kshitiz Bansal
B.Tech CSE (AIML)

⸻

⭐ Support

If you found this project useful:
	•	⭐ Star this repository
	•	🍴 Fork and improve

⸻

📜 License

This project is for academic and educational purposes.
:::

⸻

🏆 WHAT THIS DOES FOR YOU

After adding this:
	•	Your repo looks professional
	•	Faculty sees clear understanding
	•	Recruiters see real NLP project
	•	You stand out from other students

⸻

⚡ NEXT STEP

Run:

git add README.md
git commit -m "Upgraded professional README"
git push


⸻

If you want next level:
👉 I can add architecture diagram + deployment link (live demo) 🚀
