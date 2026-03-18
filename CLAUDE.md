# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
python app.py
# Serves at http://localhost:5000 (debug mode with auto-reload)
```

Required: `GOOGLE_API_KEY` in `.env` (Google Gemini API key, format `AIzaSy...`).

Install dependencies:
```bash
python -m pip install -r requirements.txt
```

## Architecture

Single-file Flask app (`app.py`) with no database or authentication. The request lifecycle is:

1. Frontend (`templates/index.html`) POSTs a URL to `/analyze`
2. `scrape_website()` fetches and parses the target URL with requests + BeautifulSoup, extracting structured signals (title, meta description, headings, about sections, nav links, award/press mentions)
3. `build_prompt()` assembles a Gemini prompt combining the scraped data with the reference database (7 examples per category from `database.py`) and a fixed JSON schema
4. `analyze_with_claude()` calls Gemini 2.5 Flash (`gemini.models.generate_content`) and returns parsed JSON
5. The JSON is returned as-is to the frontend, which renders the SVG arc score and animated progress bars

## Key design decisions

**Reference database (`database.py`)** is the scoring anchor — it contains ~150 luxury interior design studios categorized 1–5. The AI compares the scraped studio against these references to calibrate its score. Changing categories or adding studios directly affects all future analyses.

**Prompt construction**: The system prompt instructs Gemini to respond only in valid JSON. The user prompt includes the full reference database excerpts + scraped content + strict JSON schema. If the response starts with markdown fences (` ``` `), they are stripped before `json.loads()`.

**Gemini client** is initialized once at module level as `gemini = genai.Client(api_key=...)` and reused across requests. Uses `google-genai` package (not the deprecated `google-generativeai`).

**Frontend**: Single HTML file with inline JS. The SVG arc (270°, `r=54`, `viewBox 0 0 120 120`) animates via `stroke-dashoffset` transition. Progress bars animate width via staggered `setTimeout` (80ms per criterion). No build step, no framework.

## Scoring schema

The API always returns this structure:
```json
{
  "score_global": 1-5,
  "explication_globale": "...",
  "criteres": {
    "positionnement":     { "score": 1-5, "label": "...", "explication": "..." },
    "clientele_cible":    { "score": 1-5, "label": "...", "explication": "..." },
    "qualite_visuelle":   { "score": 1-5, "label": "...", "explication": "..." },
    "reputation_notoriete": { "score": 1-5, "label": "...", "explication": "..." },
    "alignement_global":  { "score": 1-5, "label": "...", "explication": "..." },
    "adequation_oeuvres": { "score": 1-5, "label": "...", "explication": "..." }
  }
}
```
