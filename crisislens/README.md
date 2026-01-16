# CrisisLens AI – Multimodal Crisis Analysis Assistant

CrisisLens AI is a full-stack demo that uses the **Gemini 3 multimodal API** to analyze crisis situations from an uploaded image and a text incident report. It returns structured emergency insights to support situational awareness.

> **Disclaimer:** Output is AI-assisted and does **not** replace professional emergency judgment.

## Features
- Responsive web interface for image upload + incident description
- FastAPI backend with a `/analyze` endpoint
- Gemini 3 multimodal prompt orchestration
- Structured JSON response with severity assessment, risks, and actions

## Architecture Overview
```
Browser (HTML/CSS/JS)
        |
        |  multipart/form-data
        v
FastAPI (/analyze)  --->  Gemini 3 Multimodal Model
        |
        v
Structured JSON response
```

## Gemini 3 Usage
The backend uses `google-generativeai` and the Gemini 3 multimodal model. It sends:
- A strict system prompt with the required JSON schema
- The incident description text
- The uploaded image (JPEG/PNG)

The model response is parsed as JSON and returned directly to the frontend.

## Local Setup

### 1) Create and activate a virtual environment (optional)
```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
```

### 2) Install backend dependencies
```bash
pip install -r crisislens/backend/requirements.txt
```

### 3) Configure environment variables
```bash
copy crisislens\backend\.env.example crisislens\backend\.env
```
Edit `crisislens/backend/.env` and set your Gemini API key.

### 4) Run the API server
```bash
uvicorn crisislens.backend.main:app --reload
```
Then open: `http://localhost:8000`

## Project Structure
```
crisislens/
  backend/
    main.py
    requirements.txt
    .env.example
  frontend/
    index.html
    styles.css
    app.js
```

## Safety & Ethics Notes
- The assistant avoids harmful, violent, or political persuasion content.
- Results are intended for **support** only; always verify with qualified emergency professionals.

## API Example
`POST /analyze` with multipart form-data fields:
- `image`: JPEG or PNG image
- `text`: incident description

### Response
```json
{
  "crisis_type": "",
  "severity_level": "Low | Medium | High | Critical",
  "key_observations": [],
  "identified_risks": [],
  "recommended_actions": []
}
```
