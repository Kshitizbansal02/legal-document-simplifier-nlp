# UI Guide

Visual and functional guide to the Legal Document Analyzer interface.

## Overall Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Header: "Legal Document Analyzer"                              │
│ Subtitle: "Analyze contracts and legal documents..."           │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────┬──────────────────────────────────────┐
│                          │                                      │
│  INPUT SECTION           │  RESULTS SECTION                     │
│  (Left Column)           │  (Right Column)                      │
│                          │                                      │
│ ┌────────────────────┐   │ ┌────────────────────────────────┐   │
│ │ [Paste Text] [Upload] │ │ Risk Badge [Medium | 45%]       │   │
│ └────────────────────┘   │ └────────────────────────────────┘   │
│                          │                                      │
│ ┌────────────────────┐   │ ┌────────────────────────────────┐   │
│ │                    │   │ Key Takeaway Section             │   │
│ │ Text Input Area    │   │ - Shows AI-generated summary     │   │
│ │ (min 100 chars)    │   │                                  │   │
│ │                    │   │ Key Risks:                       │   │
│ │                    │   │ • Risk item 1                    │   │
│ └────────────────────┘   │ • Risk item 2                    │   │
│                          │                                  │   │
│ [Analyze Button]         │ Recommended Actions:             │   │
│                          │ • Action 1                       │   │
│ Error Display (if any)   │ • Action 2                       │   │
│                          │                                  │   │
│                          │ Flagged Clauses:                 │   │
│                          │ [High Risk Clause 1]             │   │
│                          │ [Med Risk Clause 2]              │   │
│                          │                                  │   │
│                          │ Similar Clauses:                 │   │
│                          │ [92% match - Industry Std]       │   │
│                          │                                  │   │
│                          │ [Anonymized Document ▼]          │   │
│                          │                                  │   │
│                          │ (Scrollable for long content)    │   │
└──────────────────────────┴──────────────────────────────────────┘
```

## Input Section

### Text Input Mode

```
┌─ Paste Text ─┬─ Upload File ─┐
│                              │
│ Paste Document Text          │
│ 0 characters (min 100 req)   │ ← Character counter
│                              │
│ ┌──────────────────────────┐ │
│ │                          │ │
│ │  Paste your legal        │ │
│ │  document text here...   │ │
│ │                          │ │
│ │                          │ │
│ └──────────────────────────┘ │ ← Textarea
│                              │
│ [    Analyze Document    ]   │ ← Button (disabled if < 100 chars)
│                              │
```

**States:**
- ⚪ **Idle**: Textarea empty, button disabled
- 🔵 **Ready**: Text ≥100 chars, button enabled
- ⏳ **Loading**: Button shows spinner, disabled
- ❌ **Error**: Message appears below button

### File Upload Mode

```
┌─ Paste Text ─┬─ Upload File ─┐
│                              │
│ Upload Document              │
│                              │
│ ┌──────────────────────────┐ │
│ │      📄 Upload Area      │ │
│ │                          │ │
│ │  Click to upload or      │ │
│ │  drag and drop           │ │
│ │                          │ │
│ │  TXT, PDF, DOC, DOCX     │ │
│ │  up to 10MB              │ │
│ └──────────────────────────┘ │
│                              │
```

**States:**
- ⚪ **Idle**: Upload icon, placeholder text
- 📄 **Selected**: File icon, filename displayed
- ⏳ **Loading**: Spinner animation
- ❌ **Error**: Error message appears

## Results Section

### Risk Badge

```
🔴 High Risk
   67% Risk Score

OR

🟡 Medium Risk
   45% Risk Score

OR

🟢 Low Risk
   23% Risk Score
```

**Colors:**
- 🔴 Red: High risk (67-100%)
- 🟡 Amber: Medium risk (34-66%)
- 🟢 Emerald: Low risk (0-33%)

### Key Takeaway

```
💡 Key Takeaway
   This is a comprehensive document...
   Lorem ipsum dolor sit amet...
   Consider consulting legal counsel.
```

### Key Risks Section

```
Key Risks Identified

⚠️  Unlimited liability exposure
⚠️  Broad indemnification clause
⚠️  Non-compete duration questionable
```

### Recommended Actions

```
Recommended Actions

✓ Review and limit indemnification
✓ Set specific liability caps
✓ Consult with legal counsel
✓ Verify termination notice period
```

### Flagged Clauses

```
Flagged Clauses

┌─────────────────────────────────┐
│ 🔴 [HIGH RISK]                  │
│ "Seller indemnifies Buyer for   │
│  all claims without limit..."   │
│ Unlimited indemnification       │
│ exposes you to significant      │
│ liability.                      │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ 🟡 [MEDIUM RISK]                │
│ "Non-compete for 5 years..."    │
│ Duration may exceed legal       │
│ limits in some jurisdictions.   │
└─────────────────────────────────┘
```

### Similar Clauses

```
Similar Clauses in Standard Documents

┌─────────────────────────────────┐
│ 📖 "Standard indemnification    │
│    clause language..."          │
│ Source: Industry-standard NDA   │
│ 92% match                       │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ 📖 "Liability limitation         │
│    agreement..."                │
│ Source: Standard SLA Template   │
│ 78% match                       │
└─────────────────────────────────┘
```

### Anonymized Document

```
Anonymized Document ▼

┌────────────────────────────────┐
│ Click to expand                │
└────────────────────────────────┘

Anonymized Document ▲

┌────────────────────────────────┐
│ [COMPANY] agrees with          │
│ [PERSON] for the purposes of   │
│ [SERVICE TYPE] between the     │
│ dates of [DATE] and [DATE]...  │
│                                │
│ [REDACTED] shall indemnify     │
│ [REDACTED] for [AMOUNT]...     │
│                                │
│ (scrollable content)           │
└────────────────────────────────┘
```

## Empty States

### Initial State (No Analysis)

```
┌──────────────────────────────────────┐
│                                      │
│                                      │
│         No analysis yet              │
│                                      │
│  Paste a document and click          │
│  analyze to get started              │
│                                      │
│                                      │
└──────────────────────────────────────┘
```

### Error State

```
Input Section:

┌───────────────────────────────────┐
│ ❌ API connection failed            │
│    Check your backend server       │
└───────────────────────────────────┘

OR

┌───────────────────────────────────┐
│ ❌ Minimum 100 characters required │
│    Please add more content         │
└───────────────────────────────────┘
```

## Component Interactions

### Tab Switching

```
[Active: Paste Text] [Inactive: Upload File]
↓
Switch to Upload File
↓
[Inactive: Paste Text] [Active: Upload File]
```

### Loading State

```
Before Click:
[    Analyze Document    ]

After Click:
[  ⏳ Analyzing...      ] (disabled)

After Completion:
Results appear in right panel
Button becomes enabled again
```

### Mobile Layout

For screens < 1024px width:

```
┌─────────────────────────────┐
│ INPUT SECTION               │
│ ┌────────────┐              │
│ │ Textarea   │              │
│ └────────────┘              │
│ [Analyze Btn]               │
├─────────────────────────────┤
│ RESULTS SECTION             │
│ (Below input on mobile)     │
│ [Results display]           │
└─────────────────────────────┘
```

## Color Scheme

### Backgrounds
- **Main Background**: Dark Navy (#1a1f2e)
- **Card Background**: Slightly Lighter (#242d3d)
- **Input Background**: Darker (#1f2839)
- **Hover Background**: Slight transparency over card

### Text Colors
- **Primary Text**: Light Gray (#e8e8e8)
- **Secondary Text**: Medium Gray (#8b949e)
- **Accents**: Gold (#d4a574)

### Status Colors
- **High Risk**: Red (#ef4444)
- **Medium Risk**: Amber (#f59e0b)
- **Low Risk**: Emerald (#10b981)
- **Primary Action**: Gold (#d4a574)

### Borders
- **Standard Border**: Dark (#364556)
- **Focus Border**: Gold (#d4a574)
- **Danger Border**: Red (#ef4444)

## Typography

### Font Families
- **Display**: Playfair Display or serif (headings)
- **Body**: Geist or sans-serif (content)
- **Mono**: Geist Mono (code/snippets)

### Size Hierarchy
- **Page Title**: 30px, bold, serif
- **Section Title**: 18px, bold, sans-serif
- **Body Text**: 14px, regular, sans-serif
- **Small Text**: 12px, regular, sans-serif
- **Tiny Text**: 11px, regular, sans-serif

### Line Heights
- **Headings**: 1.2
- **Body**: 1.5
- **Mono/Code**: 1.6

## Spacing System

All spacing uses 4px base unit:

- **xs**: 4px
- **sm**: 8px
- **md**: 12px
- **lg**: 16px
- **xl**: 24px
- **2xl**: 32px

Examples:
- Padding in buttons: 8px 16px (sm + lg)
- Gaps between elements: 16px (lg)
- Card padding: 16px (lg)
- Section gaps: 24px (xl)

## Interactive Elements

### Buttons

**Primary Button:**
```
┌─────────────────────────┐
│  Analyze Document       │ ← Gold background
│  (Hover: Darker gold)   │
│  (Disabled: Grayed out) │
└─────────────────────────┘
```

**Tab Buttons:**
```
[Active Tab] [Inactive Tab]
 (Gold bg)    (Dark bg)
```

### Collapsible Sections

**Expanded:**
```
▲ Anonymized Document
──────────────────────
Content displayed here
```

**Collapsed:**
```
▼ Anonymized Document
(Content hidden)
```

## Accessibility Features

- **Keyboard Navigation**: Tab through all interactive elements
- **Screen Reader**: All interactive elements have ARIA labels
- **Color Contrast**: All text meets AA standards (4.5:1)
- **Focus Indicators**: Clear focus ring on interactive elements
- **Semantic HTML**: Proper heading hierarchy and semantic tags

## Responsive Breakpoints

```
Mobile (< 640px)
├─ Single column layout
├─ Stack input and results vertically
└─ Larger touch targets

Tablet (640px - 1024px)
├─ Single column (stacked)
├─ Responsive padding
└─ Adjusted typography

Desktop (> 1024px)
├─ Two column layout (1/3 - 2/3)
├─ Side-by-side input and results
└─ Full interactive experience
```

## Animation & Transitions

- **Button hover**: 150ms color transition
- **Tab switch**: 200ms fade
- **Loading spinner**: Continuous 1s rotation
- **Collapse/expand**: 200ms height transition
- **Error appearance**: 300ms slide-in

## Visual Feedback

### Hover States
- Buttons: Slight darkening of background
- Links: Color change to gold
- Cards: Subtle shadow increase
- Inputs: Border color to gold

### Focus States
- All interactive elements: 3px gold ring
- Ring offset: 0px (flush)
- Ring opacity: Full

### Disabled States
- Buttons: 50% opacity, cursor not-allowed
- Inputs: Grayed out, no interactions
- Text: Muted color

## Example Workflow

1. **User lands on page**
   - Empty state displayed
   - Paste Text tab selected by default
   - Upload File tab available

2. **User pastes text**
   - Character count updates live
   - Button becomes enabled at 100+ chars
   - Visual feedback on textarea

3. **User clicks Analyze**
   - Button shows loading spinner
   - Button becomes disabled
   - Input area grays out

4. **Results arrive**
   - Risk badge appears
   - Sections populate with data
   - Button becomes enabled again
   - User can analyze new document

5. **User explores results**
   - Scroll through sections
   - Expand anonymized document
   - View similar clauses
   - Read recommendations

## Print Styles

When printed:
- Hide input section
- Show results in single column
- Expand all collapsible sections
- Hide loading indicators
- Use black text on white
- Optimize for legibility

---

This guide provides a complete visual reference for the Legal Document Analyzer UI. All styling is implemented with Tailwind CSS and can be customized by editing the color variables in `app/globals.css`.
