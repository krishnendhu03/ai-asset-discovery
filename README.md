AI Asset Discovery

An enterprise-focused AI Asset Discovery platform that identifies AI systems
and AI-related usage across software repositories and builds an evidence-backed
inventory.

The platform is designed to discover AI functionality while providing
supporting evidence, confidence levels, and reviewable asset information rather
than relying only on keyword matches.


1. Problem

Organizations may have AI systems operating across different applications and
repositories without having a reliable inventory of where AI is being used.

Simply searching for AI-related package names or model names is not sufficient
because:

- An AI SDK may be installed but never used.
- A model name may only appear in documentation or comments.
- A repository may contain genuine AI API usage.
- A repository may contain locally trained machine-learning models.
- Model artifacts may exist without obvious source-code references.
- Different pieces of evidence may need to be combined before identifying an
  AI asset.

The goal of this project is to provide a practical approach for discovering AI
assets while reducing false positives and providing evidence.

2. Approach

The system follows an evidence-driven discovery process:

text
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
Application aggregation
    ↓
Enterprise AI inventory

The system does not treat every AI-related reference as a confirmed AI system.

Instead, evidence is evaluated to determine whether the repository contains:

Actual AI usage
Machine-learning model execution
AI API usage
Model artifacts
Potential AI references
AI dependencies without recognized execution

This approach allows the system to distinguish stronger evidence from weaker
signals.

3. AI Asset Discovery

The discovery engine analyzes repository content for signals such as:

AI/ML libraries and SDKs
Provider references
Model references
AI API calls
Import statements
Dependency declarations
Machine-learning training calls
Machine-learning prediction calls
Model loading
Trained model artifacts
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
Tools
Discovery source
Category
Supporting evidence
Currently recognized AI/ML technologies

The discovery engine currently includes patterns for technologies such as:

OpenAI
Anthropic
Hugging Face Transformers
PyTorch
TensorFlow
Scikit-learn
LangChain
Model execution

The scanner detects patterns such as:

predict()
predict_proba()
fit()
fit_transform()
Model loading

The scanner detects trained models loaded using mechanisms such as:

joblib
pickle
Model artifacts

The scanner recognizes model artifact formats including:

.joblib
.pkl
.pickle
.pt
.pth
.h5
.keras
.onnx

4. Confidence Classification

The platform uses confidence levels to distinguish stronger evidence from weaker
signals.

High Confidence

Used when the repository contains strong evidence of actual AI or
machine-learning usage.

Examples include:

AI API invocation
        +
Actual model/API execution
        ↓
High Confidence

or:

Model loading
        +
Model prediction
        ↓
High Confidence

AI/ML library usage combined with genuine model execution can also result in
high confidence.

Medium Confidence

Used when meaningful AI-related evidence exists but does not meet the stronger
conditions for high confidence.

Examples include:

A detected model artifact
Model execution without stronger corroborating evidence
Low Confidence

Used for weaker or ambiguous signals.

Examples include:

AI/ML library detected without recognized model execution
AI-related reference without sufficient execution evidence

These cases are surfaced for review rather than automatically treated as
confirmed AI systems.

5. False-Positive & Edge-Case Handling

False-positive handling is a core part of the discovery approach.

The presence of an AI SDK alone should not automatically create a
high-confidence AI asset.

For example:

requirements.txt
       ↓
Scikit-learn dependency detected
       ↓
Source-code analysis
       ↓
No recognized AI/model execution
       ↓
Potential AI Reference
       ↓
Needs Review

Similarly, a model name appearing in source code does not automatically prove
that the model is being used.

The scanner also ignores common directories that are unlikely to provide useful
application-level evidence:

node_modules
.git
__pycache__
.venv
venv
env
.env
dist
build

Known test/reference files and backup/test model artifacts are also filtered
during application-level aggregation where appropriate.

This allows the inventory to focus on meaningful application evidence.

6. Supporting Evidence

Each discovered asset can contain evidence explaining why it was identified.

Examples include:

library_usage
OpenAI imported or referenced
model_usage
OpenAI chat completion invocation detected
model_usage
Machine-learning model prediction invocation detected
model_artifact
Trained model artifact detected: ai_assist_model.joblib

The UI exposes this evidence through the asset details panel.

Each evidence item can include:

Evidence type
Description
Repository-relative file path
Line number where applicable

For example:

incident-intelligence/backend/real_ai_usage.py
Line 5

Absolute local machine paths are intentionally removed from the UI.

Instead of displaying:

C:\Users\...\Desktop\...\sample-enterprise-environment\...

the application displays a clean repository-relative path.

This improves portability and avoids exposing machine-specific filesystem
information.

7. GitHub Repository Scanning

The platform supports scanning a GitHub repository by entering its repository
URL.

Example:

https://github.com/owner/repository

The frontend sends the repository URL to the FastAPI backend.

The backend then:

Validates the repository URL.
Verifies that the URL points to GitHub.
Creates a temporary directory.
Performs a shallow Git clone.
Analyzes the cloned repository.
Detects AI-related evidence.
Classifies discovered assets.
Calculates confidence.
Aggregates findings by application.
Returns the AI asset inventory to the frontend.
Removes the temporary cloned repository.

This allows the discovery workflow to be demonstrated against repositories
outside the local project.

Discovery source

The system distinguishes between:

Local Repository

and:

Git Repository

A local scan is reported as:

Local Repository

A GitHub scan is reported as:

Git Repository

This ensures that the UI reflects the actual source from which the discovery
was performed.

8. User Interface & Results

The frontend provides an enterprise-style AI Asset Inventory.

The inventory allows assets to be filtered by confidence:

All
High
Medium
Low

The inventory table provides:

Field	Description
Asset	Discovered AI application/system
Type	AI application, model artifact, or potential AI reference
Model	Detected model
Provider	Detected AI provider
Confidence	High, Medium, or Low
Status	Discovery/review status

Selecting an asset opens a detailed view containing:

Asset information
Confidence
Status
Type
Model
Provider
Location
Application
Purpose
Discovery source
Category
Tools
Supporting evidence

The interface also provides a Start New Repository Scan workflow with:

Local Repository
GitHub Repository


9. Test Repository

The project contains a dedicated test repository with intentionally different
discovery scenarios:

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

This provides controlled examples for evaluating discovery and false-positive
handling.

10. Sample Enterprise Environment

To demonstrate AI Asset Discovery in a realistic organizational setting,
the project includes a sample enterprise environment containing three
AI-enabled applications:

- AI Assist
- Enterprise Knowledge
- Incident Intelligence

Each application represents a different enterprise use case and contains
AI-related implementation evidence such as providers, models, SDKs,
API usage, and supporting source-code references.

The AI Asset Discovery platform scans this environment as a testbed and
identifies the AI assets operating within it.

The sample environment is not the primary product. It exists to provide a
realistic environment against which the discovery capabilities can be
demonstrated.

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

The backend contains the API, models, routes, and discovery engine.

The frontend contains the inventory interface and repository scanning workflow.

The sample enterprise environment provides controlled applications for
testing the discovery engine.

12. Technology Stack

Frontend

React.js
JavaScript
HTML5
CSS3
Vite

Backend

Python
FastAPI
Pydantic

Database

PostgreSQL
SQLAlchemy
RDBMS

Discovery

Repository analysis
Source-code analysis
Dependency analysis
AI/ML pattern detection
Model artifact detection
Evidence collection
Evidence correlation
Confidence classification
Application aggregation
False-positive handling

Version Control

Git
GitHub

13. How to Run Backend

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

Running a Local Repository Scan

From the UI:

+ New Scan
    ↓
Local Repository
    ↓
Enter repository path
    ↓
Start Scan

The resulting assets are marked:

Discovery Source:
Local Repository
Running a GitHub Repository Scan

From the UI:

+ New Scan
    ↓
GitHub Repository
    ↓
Enter GitHub repository URL
    ↓
Start Scan

The resulting assets are marked:

Discovery Source:
Git Repository

14. Example Discovery Flow

User enters repository
              ↓
        Start New Scan
              ↓
       FastAPI backend
              ↓
    Local path / Git clone
              ↓
       Repository analysis
              ↓
   Source & dependency analysis
              ↓
      Evidence extraction
              ↓
     Evidence correlation
              ↓
    Asset classification
              ↓
     Confidence scoring
              ↓
    Application aggregation
              ↓
       AI Asset Inventory
              ↓
      Supporting Evidence

The important part of the flow is that the system does not immediately
classify a repository as an AI application after finding a single keyword.

Evidence is collected first and classification happens after the evidence has
been evaluated.

15. Key Design Decisions

Evidence before classification

AI-related keywords alone are not treated as proof of an AI system.

The scanner first collects evidence and then determines how strongly that
evidence supports an AI asset.

Confidence instead of binary classification

The system distinguishes strong evidence from ambiguous evidence.

This allows reviewers to prioritize high-confidence discoveries while still
reviewing weaker signals.

False-positive handling

Unused SDKs, model references, model artifacts, and actual AI API usage are
treated differently.

This reduces the risk of creating misleading AI inventory entries.

Explainability

Supporting evidence is displayed so reviewers can understand why an asset was
discovered.

The goal is not only to say:

AI detected

but to show:

What was detected
        +
Where it was detected
        +
What type of evidence it represents
        +
How confident the discovery is
Repository-relative evidence

Machine-specific absolute paths are not exposed in the final inventory.

Evidence is normalized to repository-relative paths so that results remain
portable and easier to review.

Application-level aggregation

Multiple files and model artifacts belonging to the same application are
aggregated into an application-level AI asset.

For example:

AI Assist
    ├── train_model.py
    ├── ai_assist.py
    ├── requirements.txt
    └── ai_assist_model.joblib

can be represented as one application-level asset:

AI Assist

This makes the inventory more useful at an enterprise level.

Local and remote discovery

The same discovery engine is used for both:

Local Repository

and:

Git Repository

This keeps the discovery logic consistent regardless of how the repository
was provided.

16. Database

The platform uses PostgreSQL as its relational database.

SQLAlchemy is used as the ORM layer between the FastAPI backend and PostgreSQL.

Discovered AI assets are persisted in the `ai_assets` table, including:

- Asset ID
- Asset name
- Asset type
- Model
- Provider
- Location
- Application
- Purpose
- Tools
- Discovery source
- Status
- Category
- Confidence
- Description

The database provides persistent storage for discovered AI assets instead of relying only on in-memory application state.

17. Screenshots

The `screenshots/` directory contains screenshots demonstrating:

- AI Asset Discovery dashboard
- AI asset inventory
- Asset details and supporting evidence
- Sample enterprise environment
- AI-Assist
- Enterprise-knowledge
- Incident-intelligence

18. Outcome

The project demonstrates an end-to-end approach for:

Discovering AI assets in repositories
Scanning local repositories
Scanning GitHub repositories
Building an AI asset inventory
Detecting AI API usage
Detecting machine-learning execution
Detecting trained model artifacts
Collecting supporting evidence
Assigning confidence levels
Handling false positives and edge cases
Aggregating findings by application
Displaying repository-relative evidence paths
Identifying the actual discovery source
Reviewing discovered assets through an enterprise-style UI
Demonstrating discovery against a sample enterprise environment

The focus is not only on identifying AI-related code, but on providing
evidence-backed, explainable, and reviewable AI asset discovery.

19. Deployed Application

Live application:

[https://ai-asset-discovery.onrender.com]

Backend API:

[https://ai-asset-discovery-backend.onrender.com]

20. Demo & Evaluation

The project can be evaluated using the deployed application or by running
the project locally.

Recommended Demo Flow


1. Open the AI Asset Discovery dashboard.
2. Click **+ New Scan**.
3. Select **GitHub Repository**.
4. Enter:`https://github.com/krishnendhu03/ai-asset-discovery`
5. Click Start Scan.
6. Review the resulting AI asset inventory and confidence classifications.
7. Select **Incident Intelligence**.
8. Review its confidence, provider, model, application, purpose, and discovery source.
9. Review the **Supporting Evidence**, including repository-relative file paths
   and source-code line numbers.

Demonstrated Sample Environment

The repository contains a sample enterprise environment with:

- AI Assist
- Enterprise Knowledge
- Incident Intelligence

These applications provide realistic AI/ML usage for demonstrating the
discovery engine.

Screenshots

Screenshots demonstrating the dashboard, asset inventory, asset details,
supporting evidence, and sample enterprise environment are available in
the `screenshots/` directory.