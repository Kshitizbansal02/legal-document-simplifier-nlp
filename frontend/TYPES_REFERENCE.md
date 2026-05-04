# TypeScript Types Reference

Complete type definitions used throughout the Legal Document Analyzer application.

## Core Types

### AnalysisResult

The main response type returned after analyzing a document.

```typescript
interface AnalysisResult {
  summary: string;
  riskLevel: 'low' | 'medium' | 'high';
  riskPercentage: number;
  anonymizedText: string;
  keyRisks: string[];
  flaggedClauses: FlaggedClause[];
  similarClauses: SimilarClause[];
  recommendedActions: string[];
}
```

**Properties:**
- `summary` - Brief human-readable summary of the analysis
- `riskLevel` - Overall risk assessment (low: 0-33%, medium: 34-66%, high: 67-100%)
- `riskPercentage` - Numerical risk score from 0-100
- `anonymizedText` - Document text with PII replaced with [REDACTED]
- `keyRisks` - Array of identified risks in plain English
- `flaggedClauses` - Detailed information about problematic clauses
- `similarClauses` - Comparable clauses from standard documents
- `recommendedActions` - Suggested steps to address identified issues

**Example:**
```typescript
const result: AnalysisResult = {
  summary: "This service agreement contains moderate risk...",
  riskLevel: 'medium',
  riskPercentage: 42,
  anonymizedText: "[COMPANY] agrees to provide services to [PARTY]...",
  keyRisks: [
    'Unlimited liability exposure',
    'Broad indemnification clause'
  ],
  flaggedClauses: [...],
  similarClauses: [...],
  recommendedActions: [...]
};
```

---

### FlaggedClause

Represents a single problematic clause found in the document.

```typescript
interface FlaggedClause {
  text: string;
  riskLevel: 'low' | 'medium' | 'high';
  reason: string;
}
```

**Properties:**
- `text` - The actual clause text from the document
- `riskLevel` - Risk level specific to this clause
- `reason` - Explanation of why this clause is flagged

**Example:**
```typescript
const flagged: FlaggedClause = {
  text: "Seller indemnifies Buyer for all claims without limitation",
  riskLevel: 'high',
  reason: "Unlimited indemnification exposes you to significant liability"
};
```

---

### SimilarClause

Represents a clause from standard documents that matches content in the analyzed document.

```typescript
interface SimilarClause {
  text: string;
  relevance: number;
  source: string;
}
```

**Properties:**
- `text` - The matching clause text
- `relevance` - Similarity score from 0.0 to 1.0 (1.0 = exact match)
- `source` - Origin document type or standard (e.g., "Standard NDA")

**Example:**
```typescript
const similar: SimilarClause = {
  text: "The parties agree to maintain confidentiality...",
  relevance: 0.92,
  source: "Industry-standard NDA"
};
```

---

## Request Types

### AnalyzeRequest

Request body for analyzing plain text documents.

```typescript
interface AnalyzeRequest {
  text: string;
  docType?: string;
}
```

**Properties:**
- `text` (required) - The document text to analyze (minimum 100 characters)
- `docType` (optional) - Classification of document type (e.g., "Contract", "NDA")

**Example:**
```typescript
const request: AnalyzeRequest = {
  text: "This Agreement is entered into between...",
  docType: "Contract"
};
```

---

### FileAnalyzeRequest

Request body for analyzing uploaded files.

```typescript
interface FileAnalyzeRequest {
  fileName: string;
  content: string;
  docType?: string;
}
```

**Properties:**
- `fileName` (required) - Name of the uploaded file
- `content` (required) - File content as string
- `docType` (optional) - Document classification

**Example:**
```typescript
const request: FileAnalyzeRequest = {
  fileName: "service_agreement.pdf",
  content: "File content here...",
  docType: "Service Agreement"
};
```

---

## API Functions

### analyzeText(request: AnalyzeRequest): Promise<AnalysisResult>

Analyzes plain text documents.

**Parameters:**
- `request` - AnalyzeRequest object containing text and optional docType

**Returns:** Promise resolving to AnalysisResult

**Throws:** Error on API failure or validation error

**Example:**
```typescript
import { analyzeText } from '@/lib/api';

const result = await analyzeText({
  text: "Document text here...",
  docType: "Contract"
});

console.log(result.riskLevel);
console.log(result.flaggedClauses);
```

---

### analyzeFile(request: FileAnalyzeRequest): Promise<AnalysisResult>

Analyzes uploaded files.

**Parameters:**
- `request` - FileAnalyzeRequest object with file content

**Returns:** Promise resolving to AnalysisResult

**Throws:** Error on API failure or validation error

**Example:**
```typescript
import { analyzeFile } from '@/lib/api';

const result = await analyzeFile({
  fileName: "contract.pdf",
  content: fileContent,
  docType: "Service Agreement"
});
```

---

### getDocumentTypes(): Promise<string[]>

Fetches available document type classifications.

**Parameters:** None

**Returns:** Promise resolving to array of document type strings

**Example:**
```typescript
import { getDocumentTypes } from '@/lib/api';

const types = await getDocumentTypes();
// ['Contract', 'NDA', 'Employment Agreement', ...]
```

---

## Component Props

### LegalAnalyzer

Main application component. No props required.

```typescript
export default function LegalAnalyzer() {
  // Main app component
}
```

---

### ResultsPanel

Displays analysis results.

```typescript
interface ResultsPanelProps {
  result: AnalysisResult;
}
```

**Properties:**
- `result` - The AnalysisResult to display

**Example:**
```tsx
<ResultsPanel result={analysisResult} />
```

---

### RiskBadge

Displays risk level with visual indicator.

```typescript
interface RiskBadgeProps {
  riskLevel: 'low' | 'medium' | 'high';
  percentage?: number;
}
```

**Properties:**
- `riskLevel` - The risk level to display
- `percentage` (optional) - Risk score as percentage

**Example:**
```tsx
<RiskBadge riskLevel="medium" percentage={45} />
```

---

### TextInputSection

Text input component.

```typescript
interface TextInputSectionProps {
  value: string;
  onChange: (value: string) => void;
  onAnalyze: () => void;
  isLoading: boolean;
  placeholder?: string;
}
```

**Properties:**
- `value` - Current textarea value
- `onChange` - Callback when text changes
- `onAnalyze` - Callback when analyze button is clicked
- `isLoading` - Whether analysis is in progress
- `placeholder` (optional) - Textarea placeholder text

---

### FileUploadSection

File upload component.

```typescript
interface FileUploadSectionProps {
  onFileSelect: (file: File) => void;
  isLoading: boolean;
}
```

**Properties:**
- `onFileSelect` - Callback when file is selected
- `isLoading` - Whether analysis is in progress

---

### SimplifiedExplanation

Summary explanation display.

```typescript
interface SimplifiedExplanationProps {
  summary: string;
}
```

**Properties:**
- `summary` - The explanation text to display

---

### FlaggedClausesSection

Displays flagged clauses list.

```typescript
interface FlaggedClausesSectionProps {
  clauses: FlaggedClause[];
}
```

**Properties:**
- `clauses` - Array of FlaggedClause objects

---

### SimilarClausesSection

Displays similar clauses from standards.

```typescript
interface SimilarClausesSectionProps {
  clauses: SimilarClause[];
}
```

**Properties:**
- `clauses` - Array of SimilarClause objects

---

### KeyRisksSection

Displays key risks list.

```typescript
interface KeyRisksSectionProps {
  risks: string[];
}
```

**Properties:**
- `risks` - Array of risk descriptions

---

### RecommendedActionsSection

Displays recommended actions.

```typescript
interface RecommendedActionsSectionProps {
  actions: string[];
}
```

**Properties:**
- `actions` - Array of action recommendations

---

### AnonymizedTextCollapsible

Collapsible anonymized text viewer.

```typescript
interface AnonymizedTextCollapsibleProps {
  text: string;
}
```

**Properties:**
- `text` - The anonymized document text

---

## Risk Level Constants

```typescript
type RiskLevel = 'low' | 'medium' | 'high';

// Risk ranges (percentages)
const RISK_RANGES = {
  LOW: { min: 0, max: 33 },
  MEDIUM: { min: 34, max: 66 },
  HIGH: { min: 67, max: 100 }
};

// Risk colors
const RISK_COLORS = {
  low: '#10b981', // emerald
  medium: '#f59e0b', // amber
  high: '#ef4444' // red
};
```

---

## Error Handling

All API functions may throw errors that should be caught:

```typescript
try {
  const result = await analyzeText({ text: documentText });
} catch (error) {
  if (error instanceof Error) {
    console.error('Analysis failed:', error.message);
    // Handle error appropriately
  }
}
```

Common error scenarios:
- `text` or `content` is less than 100 characters
- API server is unreachable
- API returns non-200 status code
- Response doesn't match expected structure

---

## Environment Variables

### NEXT_PUBLIC_API_URL

**Type:** `string`
**Default:** `http://localhost:8000`
**Description:** Backend API base URL

```typescript
// Automatically used in API functions
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

---

## Utility Types

### Optional Properties

Many types use optional properties (marked with `?`):

```typescript
interface AnalyzeRequest {
  text: string;        // Required
  docType?: string;    // Optional
}
```

### Discriminated Unions

Risk levels are discriminated unions for type safety:

```typescript
type RiskLevel = 'low' | 'medium' | 'high';

function handleRisk(level: RiskLevel) {
  switch (level) {
    case 'low':
      // ...
    case 'medium':
      // ...
    case 'high':
      // ...
  }
}
```

---

## Usage Examples

### Complete Analysis Flow

```typescript
import { analyzeText, AnalysisResult } from '@/lib/api';
import { FlaggedClause, SimilarClause } from '@/lib/types';

async function analyzeDocument(text: string) {
  try {
    // Analyze
    const result: AnalysisResult = await analyzeText({
      text: text,
      docType: 'Contract'
    });

    // Process results
    const riskLevel = result.riskLevel; // 'low' | 'medium' | 'high'
    const risks: string[] = result.keyRisks;
    const flagged: FlaggedClause[] = result.flaggedClauses;
    const similar: SimilarClause[] = result.similarClauses;
    const actions: string[] = result.recommendedActions;

    // Display or process further
    console.log(`Risk Level: ${riskLevel} (${result.riskPercentage}%)`);
    risks.forEach(risk => console.log(`- ${risk}`));

  } catch (error) {
    console.error('Failed to analyze:', error);
  }
}
```

---

## Type Checking

This project uses TypeScript with strict mode enabled. All types are fully checked at compile time:

```typescript
// This will cause a TypeScript error
const result: AnalysisResult = {
  summary: "...",
  riskLevel: 'invalid', // Error: Type '"invalid"' is not assignable
  // ...
};

// This is correct
const result: AnalysisResult = {
  summary: "...",
  riskLevel: 'medium', // OK
  // ...
};
```
