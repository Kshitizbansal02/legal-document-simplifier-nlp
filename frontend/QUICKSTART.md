# Quick Start Guide

Get the Legal Document Analyzer up and running in 5 minutes.

## 1. Prerequisites

- Node.js 18+ ([Download](https://nodejs.org/))
- pnpm ([Installation](https://pnpm.io/installation)) or npm

## 2. Setup

### Clone/Extract the Project
```bash
cd legal-document-analyzer
```

### Install Dependencies
```bash
pnpm install
```

### Configure Backend URL
```bash
# Create .env.local file
cp .env.example .env.local

# For local development, the default is already set:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 3. Start Development Server

```bash
pnpm dev
```

The application will open at **http://localhost:3000**

## 4. Setup Backend (Optional for Local Testing)

To fully test the application, you need a backend API. Create a simple Python Flask backend:

### Install Flask
```bash
pip install flask flask-cors
```

### Create Backend Script (`backend.py`)

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    text = data.get('text', '')
    
    return jsonify({
        'summary': 'This document analysis is a demonstration.',
        'riskLevel': 'medium',
        'riskPercentage': 45,
        'anonymizedText': '[REDACTED] agrees with [REDACTED]',
        'keyRisks': ['Potential liability exposure', 'Broad indemnification'],
        'flaggedClauses': [
            {
                'text': 'Indemnification clause',
                'riskLevel': 'high',
                'reason': 'Could expose you to significant liability'
            }
        ],
        'similarClauses': [
            {
                'text': 'Standard indemnification language',
                'relevance': 0.87,
                'source': 'Industry Standard NDA'
            }
        ],
        'recommendedActions': [
            'Review indemnification limits',
            'Add caps to liability',
            'Consult legal counsel'
        ]
    })

@app.route('/api/analyze-file', methods=['POST'])
def analyze_file():
    return analyze()

@app.route('/api/doc-types', methods=['GET'])
def doc_types():
    return jsonify(['Contract', 'NDA', 'Employment Agreement', 'Service Agreement'])

if __name__ == '__main__':
    app.run(debug=True, port=8000)
```

### Run Backend
```bash
python backend.py
```

The backend will run at **http://localhost:8000**

## 5. Test the Application

### Using Text Input
1. Go to http://localhost:3000
2. Make sure "Paste Text" tab is selected
3. Paste a legal document (minimum 100 characters)
4. Click "Analyze Document"
5. View results on the right panel

### Using File Upload
1. Click "Upload File" tab
2. Select or drag a TXT file
3. Results appear automatically

## 6. Customization

### Change Colors/Theme
Edit `app/globals.css`:

```css
:root {
  --primary: #d4a574;      /* Gold - Change this */
  --background: #1a1f2e;   /* Dark Navy - Change this */
  --accent: #6ba3d4;       /* Blue - Change this */
  /* ... other colors */
}
```

### Change API URL for Production
Update `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

### Add Document Types
1. Update backend to return more types
2. Frontend automatically uses them in the UI

## 7. Build for Production

```bash
pnpm build
pnpm start
```

Or deploy to Vercel:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

## 8. Troubleshooting

### "API connection failed"
- Check backend is running at http://localhost:8000
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check browser console (F12) for errors

### "Cannot find module"
```bash
# Clear and reinstall
rm -rf node_modules
pnpm install
```

### Port 3000 Already in Use
```bash
# Run on different port
pnpm dev -- -p 3001
```

## 9. Project Structure

```
├── app/
│   ├── layout.tsx          # Main layout
│   ├── page.tsx            # Home page
│   └── globals.css         # Theme & styles
├── components/
│   └── legal/
│       ├── LegalAnalyzer.tsx        # Main component
│       ├── TextInputSection.tsx     # Text input
│       ├── FileUploadSection.tsx    # File upload
│       ├── ResultsPanel.tsx         # Results display
│       └── ... (other components)
├── lib/
│   ├── api.ts              # API integration
│   ├── types.ts            # TypeScript types
│   └── utils.ts            # Utilities
├── .env.example            # Example env vars
├── .env.local              # Your env vars
└── README.md               # Full documentation
```

## 10. Next Steps

1. **Connect Your Backend**: Implement the API analysis logic
2. **Deploy**: Push to GitHub and deploy to Vercel
3. **Customize**: Adjust colors, add document types, modify analysis
4. **Integrate ML**: Add LLM analysis (OpenAI, Claude, etc.)

## Common Customizations

### Add a New Analysis Section

1. Create component in `components/legal/NewSection.tsx`
2. Add its type to `lib/types.ts`
3. Include in `ResultsPanel.tsx`

### Change Analyze Button Color

In `components/legal/TextInputSection.tsx`:
```tsx
className="bg-primary hover:bg-primary/90"
// Change to:
className="bg-blue-600 hover:bg-blue-700"
```

### Modify Risk Levels

In components, the risk level styling is in `getRiskColor()` methods - adjust the colors there.

## Support Resources

- **Frontend Issues**: Check browser console (F12)
- **Backend Issues**: Check terminal output for backend
- **TypeScript Errors**: Read error messages carefully
- **API Errors**: Verify backend response structure matches types.ts

## Performance Tips

- Use browser DevTools (F12) to check:
  - Network tab: Verify API calls succeed
  - Console: Check for error messages
  - Performance: Monitor load times

## What's Next?

- Read the full [README.md](./README.md)
- Check [BACKEND_EXAMPLE.md](./BACKEND_EXAMPLE.md) for API details
- Review [TYPES_REFERENCE.md](./TYPES_REFERENCE.md) for TypeScript types
- Deploy to production

## Quick Commands Reference

```bash
# Development
pnpm dev                 # Start dev server

# Building
pnpm build              # Create production build
pnpm start              # Run production build

# Linting
pnpm lint               # Check code

# Testing
pnpm test               # Run tests (if configured)

# Dependencies
pnpm add <package>      # Add package
pnpm remove <package>   # Remove package
```

---

Happy analyzing! 🔍📄
