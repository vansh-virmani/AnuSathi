# AGENTS.md

# AI Agent Instructions for AnuSathi

## Project Overview

AnuSathi is a portfolio-quality AI application that explains AI/ML research papers in simple Hinglish using a fine-tuned Qwen model with Retrieval-Augmented Generation (RAG).

The backend is already fully implemented.

Your responsibility is ONLY the frontend unless explicitly instructed otherwise.

---

# Project Goal

Create a polished, production-quality frontend suitable for an ML Engineer portfolio.

The application should look like a real AI SaaS product rather than a classroom assignment.

Every design and code decision should prioritize:

- Simplicity
- Readability
- Maintainability
- Professional appearance
- Clean user experience

---

# CRITICAL RULES

## Rule 1

DO NOT modify the backend.

Never modify:

- Python files
- FastAPI routes
- Services
- Qdrant logic
- Embedding logic
- FlashRank
- Prompt builders
- RAG pipeline
- Fine-tuned model
- API contracts

Treat the backend as read-only.

---

## Rule 2

Create ONLY frontend files.

Allowed:

- HTML
- CSS
- JavaScript
- Images
- Icons
- Fonts

Do not reorganize the repository.

Do not rename backend folders.

Do not move backend files.

---

## Rule 3

Never invent backend endpoints.

Use ONLY these APIs.

Upload

POST

/upload

multipart/form-data

Field

file

Returns

{
    "document_id": "...",
    "status": "success"
}

------------------------------------------------

Query

POST

/query

application/json

Body

{
    "q": "...",
    "document_id": "..."
}

Returns

{
    "question": "...",
    "answer": "...",
    "sources": [
        {
            "document_id": "...",
            "page": 1
        }
    ]
}

Never change this contract.

---

## Rule 4

Do not display raw JSON.

Convert API responses into clean UI components.

Example

Instead of

{
 "answer":"...",
 "sources":[...]
}

Render

Assistant Message

↓

Citation Cards

↓

Grouped Pages

---

## Rule 5

When multiple citations belong to the same document

Group them.

Example

Sources

📄 attention.pdf

Pages

1, 4, 5

Do not repeat the filename multiple times.

---

# Frontend Technology

Use ONLY

- HTML5
- CSS3
- Vanilla JavaScript

Use

- Fetch API

Do NOT use

- React
- Next.js
- Vue
- Angular
- Bootstrap
- Tailwind
- jQuery

Keep the frontend lightweight.

---

# UI Principles

Follow DESIGN.md exactly.

When DESIGN.md and these instructions conflict,

DESIGN.md has higher priority.

---

# Code Quality

Write modular code.

Separate:

- HTML
- CSS
- JavaScript

Use meaningful variable names.

Keep functions small.

Avoid duplicate code.

Comment only where necessary.

---

# JavaScript Principles

Prefer small reusable functions.

Avoid global variables.

Use async/await for API requests.

Handle errors gracefully.

Never leave uncaught exceptions.

---

# Upload Flow

User selects PDF

↓

Call POST /upload

↓

Store returned document_id

↓

Update Current Paper card

↓

Show success notification

Do not require page refresh.

---

# Query Flow

User types question

↓

Call POST /query

↓

Use stored document_id

↓

Receive answer

↓

Render markdown

↓

Render grouped citations

↓

Auto-scroll

---

# Error Handling

Always handle

- Network errors
- Empty input
- Invalid PDF
- Upload failure
- Backend unavailable

Display user-friendly messages.

Never expose stack traces.

---

# Accessibility

Support

- Keyboard navigation
- Visible focus states
- Good colour contrast
- Responsive layout

---

# Responsiveness

Desktop

Two-column layout

Tablet

Collapsible sidebar

Mobile

Sidebar drawer

Chat full width

---

# Performance

Keep the frontend lightweight.

Avoid unnecessary dependencies.

Avoid unnecessary animations.

Minimize DOM updates.

---

# Design Philosophy

The UI should feel similar to

- Claude
- ChatGPT
- Linear

Do NOT copy them exactly.

Take inspiration from

- spacing
- typography
- simplicity
- usability

---

# Project Branding

Application Name

AnuSathi

Subtitle

A Hinglish-friendly AI tutor that explains AI/ML research papers in simple terms.

Always preserve this branding.

---

# Repository Rules

Do not delete existing files.

Do not rename files unless requested.

Do not modify backend architecture.

Do not change API contracts.

Do not introduce new frameworks.

---

# Success Criteria

A successful implementation should:

✓ Work immediately with the existing FastAPI backend.

✓ Require no backend changes.

✓ Look like a modern AI SaaS product.

✓ Be responsive.

✓ Be clean and minimal.

✓ Be suitable for showcasing on a resume and GitHub portfolio.

The backend is considered complete.

Focus all effort on delivering an exceptional frontend experience.