AI Asset Discovery

An enterprise-focused AI Asset Discovery platform that identifies AI systems and AI-related usage across software repositories and builds an evidence-backed inventory.

1.Problem

Organizations may have AI systems operating across different applications and repositories without having a reliable inventory of where AI is being used.

Simply searching for AI-related package names or model names is not sufficient because:

-An AI SDK may be installed but never used.
-A model name may only appear in documentation or comments.
-A repository may contain genuine AI API usage.
-Different pieces of evidence may need to be combined before identifying an AI asset.

The goal of this project is to provide a practical approach for discovering AI assets while reducing false positives.

2.Approach

The system follows an evidence-driven discovery process:

```text
Repository
    ↓
Repository scanning
    ↓
File and dependency analysis
    ↓
AI-related evidence detection
    ↓
Evidence correlation
    ↓
AI asset classification
    ↓
Confidence scoring
    ↓
Enterprise AI inventory

The system does not treat every AI-related reference as a confirmed AI system.

Instead, evidence is evaluated to determine whether the repository contains:

Actual AI usage
Potential AI references
Unused AI SDKs
Model references without actual usage

3.AI Asset Discovery

The discovery engine analyzes repository content for signals such as:

AI/ML libraries and SDKs
Provider references
Model references
AI API calls
Import statements
Dependency declarations
Supporting source-code evidence

Detected information is converted into an AI asset record.

Each asset can contain:

Asset name
Asset type
Model
Provider
Confidence
Status
Location
Application
Purpose
Discovery source
Category
Supporting evidence

4. Confidence Classification

The platform uses confidence levels to distinguish stronger evidence from weaker signals.

High Confidence

Used when the repository contains strong evidence of actual AI usage.

Example:

OpenAI SDK
     +
Model reference
     +
Actual API/model invocation
Medium Confidence

Used when meaningful AI-related evidence exists but is not sufficient for a high-confidence classification.

Low Confidence

Used for weak or ambiguous signals.

Examples:

AI SDK detected but not used
Model reference without an invocation
AI-related configuration without supporting usage

These cases are surfaced for review rather than automatically treated as confirmed AI systems.

5. False-Positive & Edge-Case Handling

False-positive handling is a core part of the discovery approach.

Unused SDK
requirements.txt
       ↓
OpenAI package detected
       ↓
Source-code analysis
       ↓
No actual usage found
       ↓
Low Confidence
       ↓
Needs Review

The presence of an AI SDK alone should not automatically create a high-confidence AI asset.

Model Reference Only
Model name detected
       ↓
No AI API invocation
       ↓
Potential AI Reference
       ↓
Low Confidence
       ↓
Needs Review

This allows the system to distinguish actual AI usage from simple references.

6. Supporting Evidence

Each discovered asset can contain evidence explaining why it was identified.

Examples include:

Library usage
Model usage
Provider references
Source files
File locations

The UI exposes this evidence through the asset details panel.

This provides traceability and allows a reviewer to understand the reasoning behind a discovery instead of seeing only a final classification.

7. GitHub Repository Scanning

The platform supports scanning a GitHub repository by entering its repository URL.

Example:

https://github.com/owner/repository

The frontend sends the repository URL to the FastAPI backend.

The backend then:

Retrieves the repository.
Analyzes its files and dependencies.
Detects AI-related evidence.
Classifies discovered assets.
Calculates confidence.
Returns the AI asset inventory to the frontend.

This allows the discovery workflow to be demonstrated against repositories outside the local project.

8. User Interface & Results

The frontend provides an enterprise-style AI Asset Inventory.

The dashboard displays:

Total Assets
High Confidence
Medium Confidence
Low Confidence

The inventory table provides:

Field	Description
Asset	Discovered AI application/system
Type	AI application or potential AI reference
Model	Detected model
Provider	AI provider
Confidence	High, Medium or Low
Status	Discovery/review status

Selecting an asset opens a detailed view containing:

Asset information
Confidence
Status
Model
Provider
Location
Application
Purpose
Discovery source
Category
Supporting evidence
9. Test Repository

The project contains a dedicated test-repository with intentionally different discovery scenarios:

test-repository/
├── document_processing_service.py
├── model_reference_only.py
├── real_ai_usage.py
└── unused_sdk.py

These cases demonstrate how the discovery engine handles:

Genuine AI usage
Model references
AI SDKs that are not actually used
AI-enabled application code

This provides controlled examples for evaluating the discovery and false-positive handling.

10. Sample Enterprise Environment

The repository also contains a sample enterprise environment:

sample-enterprise-environment/
├── ai-assist/
├── enterprise-knowledge/
├── incident-intelligence/
└── platform-ui/

This represents a larger enterprise-style environment containing multiple applications.

It is included to demonstrate how AI discovery can be applied across a broader software environment rather than only a small test repository.

11. Project Structure
ai-asset-discovery/
│
├── backend/
│   └── app/
│       ├── models/
│       ├── routes/
│       └── services/
│
├── frontend/
│   ├── src/
│   └── public/
│
├── test-repository/
│
├── sample-enterprise-environment/
│   ├── ai-assist/
│   ├── enterprise-knowledge/
│   ├── incident-intelligence/
│   └── platform-ui/
│
├── .gitignore
└── README.md

12. Technology Stack
Frontend
React
JavaScript
HTML5
CSS3
Vite
Backend
Python
FastAPI
Discovery
Repository analysis
Source-code analysis
Dependency analysis
Evidence correlation
Confidence classification
False-positive handling
Version Control
Git
GitHub
13. How to Run
Backend

From the project root:

cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003

Backend:

http://127.0.0.1:8003
Frontend

Open another terminal:

cd frontend
npm install
npm run dev

Open the URL provided by Vite.

14. Example Discovery Flow
User enters GitHub repository URL
              ↓
        Start New Scan
              ↓
       FastAPI backend
              ↓
      Repository retrieval
              ↓
       Repository analysis
              ↓
      Evidence extraction
              ↓
     Evidence correlation
              ↓
    Confidence classification
              ↓
       AI Asset Inventory
              ↓
      Supporting Evidence
      
15. Key Design Decisions
Evidence before classification

AI-related keywords alone are not treated as proof of an AI system.

Confidence instead of binary classification

The system distinguishes strong evidence from ambiguous evidence.

False-positive handling

Unused SDKs and model references are treated differently from actual AI API usage.

Explainability

Supporting evidence is displayed so reviewers can understand why an asset was discovered.

Enterprise inventory

The result is presented as an inventory of AI assets rather than simply a list of matching files.

16. Outcome

The project demonstrates an end-to-end approach for:

Discovering AI assets in repositories
Scanning GitHub repositories
Building an AI asset inventory
Collecting supporting evidence
Assigning confidence levels
Handling false positives and edge cases
Reviewing discovered assets through an enterprise-style UI
Demonstrating discovery against a sample enterprise environment

The focus is not only on identifying AI-related code, but on providing evidence-backed and reviewable AI asset discovery.