import base64
import io
import os
from pathlib import Path

import anthropic
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

app = FastAPI(title="Coin & Currency Identifier")

STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

ANALYSIS_PROMPT = """You are a world-class numismatist (coin/currency expert) and appraiser with decades of experience grading and valuing coins and paper currency.

Analyze this image carefully and provide a detailed assessment. Respond with ONLY valid JSON in this exact structure:

{
  "identified": true,
  "type": "coin" | "paper_currency" | "token" | "medal" | "unknown",
  "name": "Full name of the coin/currency",
  "country": "Country of origin",
  "denomination": "Face value with currency symbol",
  "year": "Year or date range (e.g. 1965 or 1965-1970)",
  "composition": "Metal composition or paper type",
  "series": "Series, edition, or mint mark details if identifiable",
  "condition": {
    "grade": "Grade abbreviation (e.g. MS-65, VF-30, XF-45, AG-3)",
    "label": "Full grade label (e.g. Mint State, Very Fine, Extremely Fine)",
    "description": "2-3 sentence description of the specific condition observed in this photo — note any wear, luster, marks, color, or damage visible"
  },
  "value": {
    "low": 0.00,
    "mid": 0.00,
    "high": 0.00,
    "currency": "USD",
    "basis": "Brief explanation of value basis (e.g. common date, key date, low mintage, error coin, historical significance)"
  },
  "notable_features": ["List", "of", "notable", "features", "or", "varieties"],
  "confidence": "high" | "medium" | "low",
  "notes": "Any important caveats, alternative identifications, or advice for professional grading"
}

Grading scale reference:
- AG-3 (About Good): heavily worn, barely identifiable
- G-4 to G-6 (Good): major features visible but flat
- VG-8 to VG-10 (Very Good): design clear but worn
- F-12 to F-15 (Fine): moderate even wear on high points
- VF-20 to VF-35 (Very Fine): light to moderate wear, all features sharp
- EF/XF-40 to EF/XF-45 (Extremely Fine): slight wear on high points only
- AU-50 to AU-58 (About Uncirculated): traces of wear on highest points
- MS-60 to MS-70 (Mint State): no wear — use sub-grades for luster/marks
- PR/PF-60 to PR/PF-70 (Proof): specially struck collector coins

For value estimation, consider the coin's grade, mintage, demand, and current market. Provide realistic USD ranges based on today's numismatic market.

If the image does not show a coin or currency, set "identified" to false and "type" to "unknown", and set value fields to 0.
"""


def process_image(image_bytes: bytes, media_type: str) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGB")
    max_size = 1568
    if max(img.size) > max_size:
        ratio = max_size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=92)
    return base64.standard_b64encode(output.getvalue()).decode("utf-8")


@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.post("/analyze")
async def analyze_coin(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await file.read()
    if len(image_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be under 20MB")

    try:
        b64_image = process_image(image_bytes, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process image: {e}")

    try:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": b64_image,
                            },
                        },
                        {"type": "text", "text": ANALYSIS_PROMPT},
                    ],
                }
            ],
        )
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid Anthropic API key")
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit reached, please try again shortly")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {e}")

    raw_text = next(
        (b.text for b in response.content if b.type == "text"), ""
    )

    import json
    import re

    json_match = re.search(r"\{[\s\S]*\}", raw_text)
    if not json_match:
        raise HTTPException(status_code=502, detail="Could not parse AI response")

    try:
        result = json.loads(json_match.group())
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="Invalid JSON in AI response")

    return JSONResponse(content=result)
