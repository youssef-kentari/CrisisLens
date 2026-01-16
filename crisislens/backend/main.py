import json
import os
from io import BytesIO
from typing import Any, Dict, Optional

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - fallback if dependency missing
    load_dotenv = None

try:
    import google.generativeai as genai
except ModuleNotFoundError:  # pragma: no cover - fallback if dependency missing
    genai = None

try:
    import multipart  # type: ignore
    multipart_available = True
except ModuleNotFoundError:  # pragma: no cover - fallback if dependency missing
    multipart_available = False

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

if load_dotenv:
    load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

missing_reason: Optional[str] = None
model = None

if not genai:
    missing_reason = "Gemini SDK not installed. Run: pip install -r crisislens/backend/requirements.txt"
elif not GEMINI_API_KEY:
    missing_reason = "GEMINI_API_KEY is not set. Add it to your environment or .env file."
else:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)

app = FastAPI(title="CrisisLens AI")

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(frontend_dir, "index.html"))


SYSTEM_PROMPT = """
You are CrisisLens AI, an emergency analysis assistant.
Analyze the provided image and text about a crisis.
Return STRICT JSON ONLY with the following schema:
{
  "crisis_type": "",
  "severity_level": "Low | Medium | High | Critical",
  "key_observations": [],
  "identified_risks": [],
  "recommended_actions": []
}
Guidelines:
- Combine visible damage and textual context.
- Be concise and factual.
- Avoid harmful, violent, or political persuasion content.
- Include an AI-assisted disclaimer in recommended_actions if appropriate.
""".strip()


def _parse_json_response(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Attempt to extract JSON substring if the model adds extra text
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise ValueError("Model returned invalid JSON.")


if multipart_available:

    @app.post("/analyze")
    async def analyze_crisis(
        image: UploadFile = File(...),
        text: str = Form(...),
    ):
        if missing_reason:
            raise HTTPException(status_code=503, detail=missing_reason)

        if image.content_type not in {"image/jpeg", "image/png"}:
            raise HTTPException(status_code=400, detail="Only JPEG and PNG images are supported.")

        image_bytes = await image.read()
        try:
            pil_image = Image.open(BytesIO(image_bytes))
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid image file.") from exc

        prompt = f"""
{SYSTEM_PROMPT}

Text context:
{text}
""".strip()

        try:
            response = model.generate_content([prompt, pil_image])
            parsed = _parse_json_response(response.text)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return JSONResponse(content=parsed)

else:

    @app.post("/analyze")
    async def analyze_crisis_unavailable():
        raise HTTPException(
            status_code=503,
            detail="python-multipart is not installed. Run: pip install -r crisislens/backend/requirements.txt",
        )


@app.get("/health")
def health_check():
    return {"status": "ok"}
