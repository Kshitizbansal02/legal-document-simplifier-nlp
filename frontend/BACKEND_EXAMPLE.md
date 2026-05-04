# Backend API Example

This document provides a reference implementation for the backend API that the Legal Document Analyzer expects.

## Quick Start with Python Flask

Here's a minimal example of how to create the required API endpoints:

### Installation

```bash
pip install flask flask-cors
```

### Implementation

Create a file `app.py`:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Mock analysis function - replace with your actual ML/AI logic
def analyze_document(text: str, doc_type: str = None) -> dict:
    """
    Analyzes a document and returns risk assessment and insights.
    Replace this with your actual analysis logic using LLMs, 
    traditional NLP, or ML models.
    """
    
    risk_score = 35  # Example: calculate based on content
    risk_level = 'medium' if risk_score > 30 else 'low'
    
    return {
        'summary': 'This is a sample contract agreement. Review the flagged clauses and recommended actions carefully.',
        'riskLevel': risk_level,
        'riskPercentage': risk_score,
        'anonymizedText': text.replace('Company', '[COMPANY]').replace('John', '[PERSON]'),
        'keyRisks': [
            'Unlimited liability clause detected',
            'Non-compete clause may be too broad',
            'Termination notice period is shorter than industry standard'
        ],
        'flaggedClauses': [
            {
                'text': 'Seller shall indemnify Buyer for any and all claims...',
                'riskLevel': 'high',
                'reason': 'Unlimited indemnification can expose you to significant liability'
            },
            {
                'text': 'Employee agrees not to compete for 5 years...',
                'riskLevel': 'medium',
                'reason': 'Non-compete duration may exceed legal limits in some jurisdictions'
            }
        ],
        'similarClauses': [
            {
                'text': 'Seller shall indemnify Buyer for losses arising from breach...',
                'relevance': 0.87,
                'source': 'Standard B2B Services Agreement'
            },
            {
                'text': 'Neither party shall be liable for indirect damages...',
                'relevance': 0.72,
                'source': 'Industry-standard NDA'
            }
        ],
        'recommendedActions': [
            'Add caps to indemnification clauses',
            'Review non-compete duration with legal counsel',
            'Ensure termination notice aligns with employment laws',
            'Add dispute resolution clause'
        ]
    }

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze text document"""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text field'}), 400
    
    text = data.get('text', '')
    doc_type = data.get('docType')
    
    if len(text) < 100:
        return jsonify({'error': 'Text too short. Minimum 100 characters required.'}), 400
    
    try:
        result = analyze_document(text, doc_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-file', methods=['POST'])
def analyze_file():
    """Analyze uploaded file"""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Missing content field'}), 400
    
    content = data.get('content', '')
    file_name = data.get('fileName', 'unknown')
    doc_type = data.get('docType')
    
    if len(content) < 100:
        return jsonify({'error': 'File content too short.'}), 400
    
    try:
        result = analyze_document(content, doc_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/doc-types', methods=['GET'])
def get_doc_types():
    """Get available document types"""
    return jsonify([
        'Contract',
        'NDA',
        'Employment Agreement',
        'Service Agreement',
        'License Agreement',
        'Purchase Agreement',
        'Lease Agreement',
        'Loan Agreement',
        'Other'
    ])

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
```

### Run the server

```bash
python app.py
```

The API will be available at `http://localhost:8000`

## Using with AI/ML Models

### With OpenAI/Claude

```python
import openai
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

def analyze_with_llm(text: str, doc_type: str = None) -> dict:
    """Use an LLM to analyze the document"""
    
    prompt = f"""Analyze this legal document and provide:
1. A brief summary (2-3 sentences)
2. Risk level (low/medium/high) with percentage
3. Key risks (list)
4. Any flagged clauses with risk level and reason
5. Recommended actions

Document:
{text}

Respond in JSON format."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    
    # Parse response and structure it
    result_text = response.choices[0].message.content
    # Parse JSON and return structured data
    return parse_llm_response(result_text)
```

### With Hugging Face Models

```python
from transformers import pipeline

def analyze_with_huggingface(text: str) -> dict:
    """Use Hugging Face models for analysis"""
    
    # Zero-shot classification for risk level
    classifier = pipeline("zero-shot-classification", 
                         model="facebook/bart-large-mnli")
    
    result = classifier(text, ["high risk", "medium risk", "low risk"])
    risk_level = result['labels'][0].split()[0].lower()
    
    # Use other models for specific tasks
    # e.g., NER for identifying parties, amounts, dates
    # e.g., Text summarization for summary
    
    return {
        'summary': 'Analysis result',
        'riskLevel': risk_level,
        'riskPercentage': 35,
        # ... other fields
    }
```

## API Response Structure

All endpoints should return the following structure:

```json
{
  "summary": "Brief explanation of the document and key findings",
  "riskLevel": "low|medium|high",
  "riskPercentage": 25,
  "anonymizedText": "Document with PII replaced with [REDACTED]",
  "keyRisks": [
    "Risk description 1",
    "Risk description 2"
  ],
  "flaggedClauses": [
    {
      "text": "The problematic clause text",
      "riskLevel": "high|medium|low",
      "reason": "Why this is a problem"
    }
  ],
  "similarClauses": [
    {
      "text": "Similar clause from standard documents",
      "relevance": 0.85,
      "source": "Document type or industry standard"
    }
  ],
  "recommendedActions": [
    "Suggested action 1",
    "Suggested action 2"
  ]
}
```

## Production Considerations

### Security
- Validate and sanitize all inputs
- Implement rate limiting
- Use HTTPS only
- Authenticate requests (OAuth2, API keys)
- Log sensitive data carefully

### Performance
- Implement caching for repeated analyses
- Use async processing for large documents
- Queue long-running tasks
- Monitor API response times

### Reliability
- Add error handling and logging
- Implement retries for external API calls
- Use database for storing analysis history
- Monitor system health

### Scalability
- Use load balancing for multiple instances
- Consider serverless functions (AWS Lambda, Azure Functions)
- Use background workers (Celery, RQ) for heavy processing
- Cache results in Redis

## Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

ENV FLASK_APP=app.py
EXPOSE 8000

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]
```

Create `requirements.txt`:

```
Flask==3.0.0
flask-cors==4.0.0
```

Build and run:

```bash
docker build -t legal-analyzer-api .
docker run -p 8000:8000 legal-analyzer-api
```

## Testing the API

```bash
# Test text analysis
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a comprehensive service agreement between Party A and Party B...",
    "docType": "Contract"
  }'

# Test document types
curl http://localhost:8000/api/doc-types

# Health check
curl http://localhost:8000/health
```

## Next Steps

1. **Implement actual analysis logic** using LLMs, ML models, or rule-based systems
2. **Add database** to store analysis history and results
3. **Implement authentication** for API security
4. **Add file processing** for PDF, DOCX formats (use `pypdf`, `python-docx`)
5. **Add caching** for frequently analyzed documents
6. **Set up monitoring** and logging
7. **Deploy to production** using Docker, Kubernetes, or serverless platforms

## Resources

- [OpenAI API Docs](https://platform.openai.com/docs)
- [Claude API Docs](https://www.anthropic.com/api)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Docs](https://docs.docker.com/)
