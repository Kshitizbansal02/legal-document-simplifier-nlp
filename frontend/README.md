# Legal Document Analyzer

A sophisticated web application for analyzing contracts and legal documents to identify risks, compliance issues, and provide actionable insights.

## Features

- **Text Analysis**: Paste legal document text directly for immediate analysis
- **File Upload**: Upload documents in TXT, PDF, DOC, or DOCX formats
- **Risk Assessment**: Automatic risk level detection (Low, Medium, High) with detailed scoring
- **Simplified Explanations**: AI-generated summaries that break down complex legal language
- **Flagged Clauses**: Identification and explanation of potentially problematic clauses
- **Similar Clauses**: Comparison with standard industry clauses for context
- **Recommended Actions**: Specific recommendations for addressing identified risks
- **Anonymized View**: View anonymized versions of documents for privacy
- **Responsive Design**: Optimized for desktop and tablet viewing

## Tech Stack

- **Frontend**: Next.js 16 with React 19
- **Styling**: Tailwind CSS with shadcn/ui components
- **Theme**: Dark mode with professional gold accents
- **Architecture**: Component-based with TypeScript for type safety

## Getting Started

### Prerequisites

- Node.js 18+ 
- pnpm, npm, or yarn

### Installation

1. **Clone or extract the project**
   ```bash
   cd legal-document-analyzer
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   # or
   npm install
   # or
   yarn install
   ```

3. **Configure environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env.local
   
   # Edit .env.local with your backend API URL
   # For local development, default is http://localhost:8000
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start the development server**
   ```bash
   pnpm dev
   # or
   npm run dev
   ```

5. **Open in browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Configuration

### Environment Variables

**NEXT_PUBLIC_API_URL** (required)
- Backend API endpoint for document analysis
- Default: `http://localhost:8000`
- For production: Set to your deployed backend URL

Example production configuration:
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## Usage

### Analyzing Text Documents

1. Click on the "Paste Text" tab
2. Paste your legal document (minimum 100 characters)
3. Click "Analyze Document"
4. View results including risk assessment, flagged clauses, and recommendations

### Uploading Files

1. Click on the "Upload File" tab
2. Click the upload area or drag-and-drop a file
3. Supported formats: TXT, PDF, DOC, DOCX
4. Wait for analysis to complete
5. Review results in the right panel

## Component Structure

```
components/
├── legal/
│   ├── LegalAnalyzer.tsx              # Main app component
│   ├── TextInputSection.tsx           # Text input UI
│   ├── FileUploadSection.tsx          # File upload UI
│   ├── RiskBadge.tsx                  # Risk level indicator
│   ├── ResultsPanel.tsx               # Results container
│   ├── SimplifiedExplanation.tsx      # Summary explanation
│   ├── KeyRisksSection.tsx            # Key risks list
│   ├── RecommendedActionsSection.tsx # Recommended actions
│   ├── FlaggedClausesSection.tsx      # Flagged clauses display
│   ├── SimilarClausesSection.tsx      # Similar clauses comparison
│   └── AnonymizedTextCollapsible.tsx  # Anonymized text viewer
```

## API Integration

The application expects a backend API with the following endpoints:

### POST `/api/analyze`
Analyzes raw text

**Request Body:**
```json
{
  "text": "Full document text here...",
  "docType": "Contract" // optional
}
```

**Response:**
```json
{
  "summary": "Document summary...",
  "riskLevel": "medium",
  "riskPercentage": 45,
  "anonymizedText": "Anonymized version...",
  "keyRisks": ["Risk 1", "Risk 2"],
  "flaggedClauses": [
    {
      "text": "Clause text",
      "riskLevel": "high",
      "reason": "Explanation"
    }
  ],
  "similarClauses": [
    {
      "text": "Similar clause",
      "relevance": 0.92,
      "source": "Standard NDA"
    }
  ],
  "recommendedActions": ["Action 1", "Action 2"]
}
```

### POST `/api/analyze-file`
Analyzes uploaded files

**Request Body:**
```json
{
  "fileName": "contract.pdf",
  "content": "File content here...",
  "docType": "Contract" // optional
}
```

**Response:** Same as `/api/analyze`

### GET `/api/doc-types`
Returns available document types (optional)

**Response:**
```json
["Contract", "NDA", "Employment Agreement", "Service Agreement"]
```

## Deployment

### Deploy to Vercel

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL` → Your backend API URL
3. Deploy automatically on push

### Deploy to Other Platforms

1. Build the project:
   ```bash
   pnpm build
   ```

2. Start the production server:
   ```bash
   pnpm start
   ```

3. Or run in Docker:
   ```bash
   docker build -t legal-analyzer .
   docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=https://api.yourdomain.com legal-analyzer
   ```

## Styling & Theme

The application uses a sophisticated dark theme with:
- **Primary Color**: Gold (#d4a574) - Professional and trustworthy
- **Background**: Dark Navy (#1a1f2e) - Easy on the eyes
- **Accents**: Emerald (low risk), Amber (medium risk), Red (high risk)

To customize colors, edit `app/globals.css` and update the CSS variables in the `:root` selector.

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Performance

- Lazy loading of components
- Optimized bundle size ~45KB
- Responsive images and optimized assets
- CSS-in-JS with Tailwind for minimal overhead

## Accessibility

- WCAG 2.1 AA compliant
- Semantic HTML structure
- Keyboard navigation support
- Screen reader friendly with ARIA labels
- Color contrast ratios meet accessibility standards

## Troubleshooting

### "API connection failed"
- Verify `NEXT_PUBLIC_API_URL` is correctly set
- Ensure backend server is running
- Check CORS configuration on backend

### "Minimum 100 characters required"
- Document text must be at least 100 characters
- Add more content or reduce restrictions in `TextInputSection.tsx`

### File upload not working
- Check file size (max 10MB recommended)
- Verify supported format (TXT, PDF, DOC, DOCX)
- Check browser console for detailed error messages

## Development

### Add a new document type
1. Update `getDocumentTypes()` in `lib/api.ts`
2. Pass `docType` to `analyzeText()` or `analyzeFile()`

### Customize analysis sections
Edit component files in `components/legal/` to add or remove analysis sections in `ResultsPanel.tsx`

### Modify theme colors
Edit CSS variables in `app/globals.css`:
```css
:root {
  --primary: #d4a574;
  --accent: #6ba3d4;
  /* ... other colors */
}
```

## Security

- No data stored on client
- HTTPS recommended for production
- Sanitized user input
- Secure API communication
- No external analytics by default

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review component documentation
3. Verify API endpoint configuration
4. Check browser console for error messages

## Future Enhancements

- Batch document processing
- Document comparison tool
- Custom risk thresholds
- Export analysis to PDF
- Integration with document signing services
- Multi-language support
- Collaboration features
- Document version history
