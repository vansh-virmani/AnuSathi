# DESIGN.md

# AnuSathi — Frontend Design Specification

> **Project**
>
> AnuSathi is a Hinglish-friendly AI tutor that explains AI/ML research papers in simple terms using a fine-tuned Qwen model with Retrieval-Augmented Generation (RAG).
>
> This document defines ONLY the frontend.
>
> The FastAPI backend, RAG pipeline, Qdrant, FlashRank, embeddings, and APIs are already complete and MUST NOT be modified.

---

# 1. Design Philosophy

The application should feel like a modern AI SaaS product.

Inspired by:

- Claude
- ChatGPT
- Linear

The UI should be:

- Clean
- Minimal
- Professional
- Academic
- Premium
- Easy to use

Avoid unnecessary dashboard elements.

Avoid flashy animations.

Prioritize excellent spacing and readability.

---

# 2. Branding

Application Name

# AnuSathi

Subtitle

> A Hinglish-friendly AI tutor that explains AI/ML research papers in simple terms.

This branding should appear at the top of the application and on the welcome screen.

---

# 3. Theme

Default Theme

Dark Mode

Provide

Dark / Light Theme Toggle

Remember the user's preference using localStorage.

---

# 4. Color Palette

## Dark Theme

Background

#0B0F17

Sidebar

#111827

Cards

#1F2937

Primary Accent

#6366F1

Success

#10B981

Primary Text

#F9FAFB

Secondary Text

#9CA3AF

Border

rgba(255,255,255,0.08)

---

## Light Theme

Background

#F8FAFC

Cards

#FFFFFF

Primary Accent

#4F46E5

Primary Text

#0F172A

Border

#E2E8F0

---

# 5. Typography

Primary Font

Inter

Fallback

system-ui

Code Font

JetBrains Mono

Use a clean typography hierarchy.

Large headings.

Comfortable paragraph spacing.

Readable markdown.

---

# 6. Overall Layout

Desktop

----------------------------------------------------

Navbar

----------------------------------------------------

Sidebar (320px)

|

Main Chat Workspace

----------------------------------------------------

Responsive

Desktop

Two-column layout

Tablet

Collapsible sidebar

Mobile

Sidebar becomes a drawer

Chat occupies full width

---

# 7. Navbar

Simple.

Minimal.

Contains only:

• Logo

• AnuSathi

• Theme Toggle

Nothing else.

Do NOT show:

- Backend Status
- API Connected
- Debug Information
- Developer Controls

---

# 8. Sidebar

The sidebar contains three sections.

----------------------------------------

Upload Paper

----------------------------------------

Large Drag & Drop Upload Area

Cloud Upload Icon

Text

Drop your research paper here

or

Browse PDF

Only PDF files accepted.

Smooth hover animation.

----------------------------------------

Current Paper

----------------------------------------

If no paper uploaded

Display

"No paper uploaded"

After upload display

📄 filename.pdf

Small badge

Active

Buttons

Remove Paper

Replace Paper

Nothing else.

Do NOT display technical information.

---

# 9. Welcome Screen

When chat is empty display a centered hero section.

--------------------------------------------------------

📄

AnuSathi

A Hinglish-friendly AI tutor that explains
AI/ML research papers in simple terms.

Upload a research paper to ask questions with citations,
or ask any AI/ML question directly.

--------------------------------------------------------

Simple.

Minimal.

Centered.

Professional.

---

# 10. Chat Experience

Messages should feel similar to Claude.

Assistant messages

Left aligned

Soft rounded card

User messages

Right aligned

Accent coloured bubble

Maximum message width around 70%.

Support Markdown.

Support

- headings
- bold
- italic
- lists
- tables
- code blocks
- syntax highlighting

Smooth fade-in animation for new messages.

Automatically scroll to newest message.

---

# 11. Input Area

Bottom fixed input.

Large rounded textarea.

Placeholder

Ask anything about AI or your uploaded paper...

Send button

Paper plane icon.

Press Enter

Send

Shift + Enter

New line

Disable input while waiting for response.

---

# 12. Upload Experience

User selects or drags a PDF.

Immediately call

POST /upload

During upload show

Uploading paper...

Extracting content...

Generating embeddings...

Indexing into Qdrant...

After success

Display a success toast

Current Paper section updates automatically.

---

# 13. AI Response Rendering

The backend returns

{
    "question": "...",
    "answer": "...",
    "sources": [...]
}

Render ONLY the answer.

Never display raw JSON.

The answer should appear as a formatted AI response.

---

# 14. Citation Rendering

When sources exist

Render a citation card below the assistant response.

Example

--------------------------------------

Sources

📄 NIPS-2017-attention-is-all-you-need-Paper.pdf

Pages: 0, 1, 4, 5

--------------------------------------

Group duplicate document names.

Merge page numbers.

Sort page numbers.

Do NOT repeat the filename multiple times.

If sources are empty

Do not display a citation section.

---

# 15. Notifications

Toast notifications.

Success

Green

Error

Red

Information

Blue

Examples

✓ Paper uploaded successfully

✕ Only PDF files are allowed

✕ Upload failed

✕ Empty question

---

# 16. Animations

Keep animations subtle.

Hover

Scale 1.02

Transition

200ms

Messages

Fade in

Typing Indicator

Three animated dots

Avoid excessive glow.

Avoid particle effects.

---

# 17. Icons

Use Lucide Icons.

Upload

Send

Trash

Moon

Sun

File

Check

Alert

Icons should be clean and modern.

---

# 18. Backend Integration

The backend is already implemented.

DO NOT modify it.

Use these APIs exactly.

Upload

POST

/upload

multipart/form-data

Field

file

Returns

{
    "document_id":"paper.pdf",
    "status":"success"
}

----------------------------------------------------

Query

POST

/query

application/json

Body

{
    "q":"What is FlashAttention?",
    "document_id":"paper.pdf"
}

Returns

{
    "question":"...",
    "answer":"...",
    "sources":[
        {
            "document_id":"paper.pdf",
            "page":5
        }
    ]
}

The frontend must consume these APIs exactly.

---

# 19. Frontend Technology

Use ONLY

- HTML
- CSS
- Vanilla JavaScript

Use

Fetch API

Do NOT use

- React
- Next.js
- Vue
- Angular
- Bootstrap
- Tailwind CSS

Keep the frontend lightweight and framework-free.

---

# 20. Accessibility

Support keyboard navigation.

Visible focus states.

Good colour contrast.

Responsive typography.

Accessible buttons and inputs.

---

# 21. Footer

Small footer.

Powered by

FastAPI • Qdrant • FlashRank • Fine-tuned Qwen

Keep it subtle.

---

# 22. Overall Goal

The finished application should feel like a real AI product rather than a student project.

A recruiter opening AnuSathi should immediately think:

"This is a polished AI application."

Prioritize:

• Simplicity

• Consistency

• Excellent spacing

• Professional UI

• Smooth user experience

The interface should look modern, trustworthy, and portfolio-ready while keeping the user's attention focused on learning from research papers.