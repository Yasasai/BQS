# Score Opportunity Page - Implementation Summary

## Overview
Successfully created and integrated the **Score Opportunity** page that allows users to assess opportunities using multiple scoring criteria with sliders, notes, and document management.

## Page Structure

### Route
- **Path:** `/score/:id`
- **Component:** `ScoreOpportunity.tsx`
- **Access:** Click "Start Assessment" from Opportunity Detail or Opportunity Inbox

### Design Features
The page maintains the same look and feel with:
- Clean white background with gray accents
- Two-column layout (scoring criteria + documents)
- Interactive sliders for scoring
- Document upload functionality
- Save Draft and Submit actions

## Scoring Criteria

### Four Assessment Categories

Each criterion includes:
- **Name/Title** - Clear category label
- **Score Slider** (0-5) - Interactive range input
- **Score Display** - Blue badge showing current score
- **Notes Field** - Textarea for detailed comments

#### 1. Fit & Strategic Alignment
- Evaluates alignment with strategic goals
- Market expansion potential
- Long-term fit assessment

#### 2. Capability & Delivery Readiness
- Team expertise evaluation
- Technology capabilities
- Resource availability
- Track record assessment

#### 3. Commercial Attractiveness
- Profit margin potential
- Pricing strategy
- Financial viability
- Competitive positioning

#### 4. Risk & Complexity
- Technical challenges
- Integration risks
- Project complexity
- Resource requirements

## Features Implemented

### ✅ Interactive Scoring
- **Range Sliders:** 0-5 scale for each criterion
- **Real-time Updates:** Score updates immediately
- **Visual Feedback:** Blue badge shows current score
- **Scale Labels:** 0-5 markers below slider

### ✅ Notes/Comments
- **Textarea for each criterion**
- **Pre-filled with sample text** (for demo)
- **Editable and saveable**
- **Supports detailed justification**

### ✅ Average Score Calculation
- **Automatic calculation** of average across all criteria
- **Displayed prominently** in blue highlight box
- **Updates in real-time** as scores change
- **Format:** X.X / 5.0

### ✅ Document Management
- **Upload Area:** Drag & drop or click to browse
- **Document List:** Shows uploaded files
- **File Details:** Name, size displayed
- **Delete Function:** Remove documents with confirmation
- **Icons:** Visual indicators for documents

### ✅ Version Information
- **Version Number:** v2.3 (Draft)
- **Created Date:** Timestamp
- **Last Saved:** Timestamp
- **Status Indicator:** Draft/Submitted

### ✅ Action Buttons
- **Save Draft:** Saves without submitting
- **Submit/Confirm:** Finalizes assessment
- **Loading States:** Shows "Saving..." or "Submitting..."
- **Disabled States:** Prevents double-submission

## Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│                        TopBar                                │
├─────────────────────────────────────────────────────────────┤
│  ← Back                                                      │
├─────────────────────────────────────────────────────────────┤
│  Score Opportunity: OPP-2023-001                            │
│  Version: v2.3 (Draft) • Created: ... • Last Saved: ...    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────┐  ┌──────────────────────────┐  │
│  │  Scoring Criteria      │  │  Version Documents       │  │
│  │  (2/3 width)           │  │  (1/3 width)             │  │
│  │                        │  │                          │  │
│  │  ┌──────────────────┐ │  │  ┌────────────────────┐  │  │
│  │  │ Fit & Strategic  │ │  │  │  Upload Area       │  │  │
│  │  │ Score: [====] 3  │ │  │  │  Drag & Drop       │  │  │
│  │  │ Notes: [......] │ │  │  └────────────────────┘  │  │
│  │  └──────────────────┘ │  │                          │  │
│  │                        │  │  Documents:              │  │
│  │  ┌──────────────────┐ │  │  • RFP_Document.pdf      │  │
│  │  │ Capability &     │ │  │  • Requirements.docx     │  │
│  │  │ Delivery         │ │  │                          │  │
│  │  │ Score: [====] 4  │ │  │  [Save Draft]            │  │
│  │  │ Notes: [......] │ │  │  [Submit / Confirm]      │  │
│  │  └──────────────────┘ │  └──────────────────────────┘  │
│  │                        │                               │
│  │  [More criteria...]    │                               │
│  │                        │                               │
│  │  Average Score: 3.0/5.0│                               │
│  └────────────────────────┘                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Navigation Flow

```
┌─────────────────────────────────────────────────────────┐
│                  Entry Points                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Opportunity Inbox                                       │
│  └── Start Assessment (action menu) ──┐                │
│                                         │                │
│  Opportunity Detail                     │                │
│  └── Start Assessment (Score tab) ─────┤                │
│                                         │                │
│                                         ▼                │
│                              /score/:id                  │
│                         ┌─────────────────┐             │
│                         │ Score Criteria  │             │
│                         │ Upload Docs     │             │
│                         │ Save/Submit     │             │
│                         └─────────────────┘             │
│                                │                         │
│                                │ Submit                  │
│                                ▼                         │
│                         Previous Page                    │
│                         (with success message)           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Data Structure

### Scoring Criteria Interface
```typescript
interface ScoringCriteria {
    id: string;              // Unique identifier
    name: string;            // Display name
    score: number;           // 0-5 score
    notes: string;           // Comments/justification
}
```

### Document Interface
```typescript
interface Document {
    id: string;              // Unique identifier
    name: string;            // File name
    size: string;            // File size (formatted)
    uploadedAt: string;      // Upload timestamp
}
```

## Actions Implemented

### 1. Score Change
```typescript
const handleScoreChange = (criteriaId: string, newScore: number) => {
    setCriteria(prev => prev.map(c => 
        c.id === criteriaId ? { ...c, score: newScore } : c
    ));
};
```

### 2. Notes Update
```typescript
const handleNotesChange = (criteriaId: string, newNotes: string) => {
    setCriteria(prev => prev.map(c => 
        c.id === criteriaId ? { ...c, notes: newNotes } : c
    ));
};
```

### 3. Save Draft
```typescript
const handleSaveDraft = async () => {
    setSaving(true);
    // TODO: POST /api/assessments (draft=true)
    console.log('Saving draft...', criteria);
    setTimeout(() => {
        setSaving(false);
        alert('Draft saved successfully!');
    }, 1000);
};
```

### 4. Submit Assessment
```typescript
const handleSubmit = async () => {
    setSaving(true);
    // TODO: POST /api/assessments (draft=false)
    console.log('Submitting assessment...', criteria);
    setTimeout(() => {
        setSaving(false);
        alert('Assessment submitted successfully!');
        navigate(-1);
    }, 1000);
};
```

### 5. File Upload
```typescript
const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
        // TODO: POST /api/opportunities/:id/documents
        console.log('Uploading files...', files);
    }
};
```

### 6. Delete Document
```typescript
const handleDeleteDocument = (docId: string) => {
    if (confirm('Are you sure you want to delete this document?')) {
        // TODO: DELETE /api/documents/:id
        setDocuments(prev => prev.filter(d => d.id !== docId));
    }
};
```

## Backend Requirements

### API Endpoints Needed

```python
# Create or update assessment
@app.post("/api/assessments")
async def create_assessment(
    opp_id: int,
    criteria: List[dict],
    is_draft: bool,
    db: Session = Depends(get_db)
):
    """
    Save assessment scores and notes
    {
        "opp_id": 123,
        "criteria": [
            {"id": "fit_strategic", "score": 3, "notes": "..."},
            {"id": "capability_delivery", "score": 4, "notes": "..."},
            ...
        ],
        "is_draft": false
    }
    """
    pass

# Get assessment for opportunity
@app.get("/api/assessments/{opp_id}")
def get_assessment(opp_id: int, db: Session = Depends(get_db)):
    """Retrieve existing assessment"""
    pass

# Upload document
@app.post("/api/opportunities/{id}/documents")
async def upload_document(
    id: int,
    file: UploadFile,
    db: Session = Depends(get_db)
):
    """Upload assessment document"""
    pass

# Delete document
@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """Delete a document"""
    pass
```

### Database Schema

```python
class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True)
    opp_id = Column(Integer, ForeignKey("opportunities.id"))
    version = Column(String)
    is_draft = Column(Boolean, default=True)
    
    # Scores
    fit_strategic_score = Column(Integer)
    fit_strategic_notes = Column(Text)
    
    capability_delivery_score = Column(Integer)
    capability_delivery_notes = Column(Text)
    
    commercial_score = Column(Integer)
    commercial_notes = Column(Text)
    
    risk_complexity_score = Column(Integer)
    risk_complexity_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(String)
    
class AssessmentDocument(Base):
    __tablename__ = "assessment_documents"
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    file_name = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String)
```

## Future Enhancements

### 1. Real-time Collaboration
- Multiple users can score simultaneously
- Live updates of scores
- Conflict resolution

### 2. Historical Comparison
- Compare with previous assessments
- Show score trends
- Highlight changes

### 3. Weighted Scoring
- Different weights for each criterion
- Configurable importance levels
- Custom calculation formulas

### 4. Approval Workflow
- Submit for review
- Approval/rejection flow
- Comments and feedback

### 5. Export Functionality
- Export assessment as PDF
- Include all scores and notes
- Attach documents

### 6. Templates
- Save scoring templates
- Reuse common notes
- Quick assessment setup

## Files Created/Modified

### Created
- ✅ `frontend/src/pages/ScoreOpportunity.tsx` - Main scoring page

### Modified
- ✅ `frontend/src/App.tsx` - Added route `/score/:id`
- ✅ `frontend/src/pages/OpportunityDetail.tsx` - Added navigation from Score tab
- ✅ `frontend/src/pages/OpportunityInbox.tsx` - Added navigation from action menu

## Testing Checklist

- [x] Page loads with valid opportunity ID
- [x] Shows loading state while fetching
- [x] All four scoring criteria display
- [x] Sliders work and update scores
- [x] Score badges update in real-time
- [x] Notes fields are editable
- [x] Average score calculates correctly
- [x] Document upload area is visible
- [x] Mock documents display
- [x] Delete document works with confirmation
- [x] Save Draft button shows loading state
- [x] Submit button shows loading state
- [x] Back button navigates correctly
- [ ] Actual save to backend (pending API)
- [ ] Actual submit to backend (pending API)
- [ ] File upload to backend (pending API)

## Complete Navigation Map

```
Application Routes:
├── / (Opportunity Inbox)
│   ├── Start Assessment → /score/:id
│   └── View Details → /opportunity/:id
│
├── /assigned-to-me (Assigned to Me)
│   └── Click Row → /opportunity/:id
│
├── /opportunity/:id (Opportunity Detail)
│   ├── Score Tab → Start Assessment → /score/:id
│   └── Back → Previous page
│
└── /score/:id (Score Opportunity)
    ├── Save Draft → Stay on page
    ├── Submit → Navigate back with success
    └── Back → Previous page
```

## Key Features Summary

### ✅ Implemented
- Interactive scoring with sliders (0-5 scale)
- Four assessment criteria with notes
- Real-time average score calculation
- Document upload interface
- Document list with delete functionality
- Save Draft functionality
- Submit/Confirm functionality
- Loading states for all actions
- Responsive two-column layout
- Consistent styling with app

### 🔄 Pending Backend Integration
- Save assessment to database
- Load existing assessment
- Upload files to server
- Delete files from server
- Version management
- User tracking

## Usage Examples

### Navigate to Score Page
```tsx
// From Opportunity Inbox
navigate(`/score/${opp.id}`);

// From Opportunity Detail
navigate(`/score/${id}`);

// Direct URL
http://localhost:5174/score/123
```

### Update Score
```tsx
<input
    type="range"
    min="0"
    max="5"
    value={criterion.score}
    onChange={(e) => handleScoreChange(criterion.id, parseInt(e.target.value))}
/>
```

### Calculate Average
```tsx
const calculateAverageScore = () => {
    const total = criteria.reduce((sum, c) => sum + c.score, 0);
    return (total / criteria.length).toFixed(1);
};
```

## Summary

The **Score Opportunity** page is now fully integrated with:
- ✅ Same look and feel as the rest of the application
- ✅ Actions matching the reference screenshot
- ✅ Interactive scoring with sliders and notes
- ✅ Document management interface
- ✅ Save Draft and Submit functionality
- ✅ Real-time average score calculation
- ✅ Seamless navigation from multiple entry points
- ✅ Professional, user-friendly interface

The page provides a comprehensive assessment workflow and is ready for backend integration to persist data and manage documents.
