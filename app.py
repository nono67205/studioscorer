"""
Studio Scorer — Flask application
Scrapes a website and uses Gemini to score it against a reference database
of luxury interior design studios.
"""

import json
import os
import re

from cerebras.cloud.sdk import Cerebras
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request

from database import get_category_descriptions, get_examples_by_category  # conservé, non utilisé

load_dotenv()

app = Flask(__name__)
cerebras = Cerebras(api_key=os.environ.get("CEREBRAS_API_KEY"))

SYSTEM_PROMPT = (
    "Tu es un consultant expert en design d'intérieur de luxe et en art contemporain. "
    "Tu évalues des studios de design pour une artiste sculptrice, Nadège Mouyssinat, "
    "qui cherche à identifier des prescripteurs potentiels pour ses œuvres. "
    "Tu réponds UNIQUEMENT en JSON valide, sans markdown, sans commentaires, "
    "sans texte avant ou après."
)

# ─────────────────────────────────────────────────────────────────────────────
# WEB SCRAPER
# ─────────────────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

ABOUT_KEYWORDS = {"about", "studio", "philosophy", "approach", "manifesto",
                  "propos", "histoire", "agence", "vision", "concept"}
AWARD_KEYWORDS = {"award", "press", "publication", "featured", "recognition",
                  "client", "prix", "presse", "paru"}


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def scrape_website(url: str) -> dict:
    """
    Scrapes the given URL and returns structured textual signals.
    Raises ValueError with a French user-friendly message on failure.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        raise ValueError("Ce site met trop de temps à répondre. Vérifiez l'URL ou réessayez.")
    except requests.exceptions.SSLError:
        raise ValueError("Erreur de certificat SSL sur ce site.")
    except requests.exceptions.ConnectionError:
        raise ValueError("Impossible de contacter ce site. Vérifiez que l'URL est correcte.")
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"Le site a retourné une erreur HTTP ({e.response.status_code}).")
    except requests.exceptions.RequestException:
        raise ValueError("Erreur réseau lors de la connexion au site.")

    try:
        soup = BeautifulSoup(resp.text, "lxml")
    except Exception:
        soup = BeautifulSoup(resp.text, "html.parser")

    # Remove script/style noise
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()

    # Title
    title = _clean(soup.title.get_text()) if soup.title else ""

    # Meta description
    meta_desc = ""
    for meta in soup.find_all("meta"):
        name = meta.get("name", "").lower()
        prop = meta.get("property", "").lower()
        if name in ("description",) or prop in ("og:description", "twitter:description"):
            meta_desc = _clean(meta.get("content", ""))
            if meta_desc:
                break

    # Headings h1–h3
    headings = [_clean(h.get_text()) for h in soup.find_all(["h1", "h2", "h3"]) if h.get_text().strip()]
    headings = list(dict.fromkeys(headings))[:20]  # deduplicate, cap at 20

    # About / philosophy sections
    about_parts = []
    for tag in soup.find_all(True):
        attrs = " ".join([
            tag.get("id", ""),
            " ".join(tag.get("class", [])),
        ]).lower()
        if any(kw in attrs for kw in ABOUT_KEYWORDS):
            text = _clean(tag.get_text())
            if len(text) > 40:
                about_parts.append(text[:500])
    about_text = " | ".join(about_parts[:5])

    # Navigation links
    nav_links = []
    for nav in soup.find_all(["nav", "header"]):
        for a in nav.find_all("a"):
            txt = _clean(a.get_text())
            if txt and len(txt) < 50:
                nav_links.append(txt)
    nav_links = list(dict.fromkeys(nav_links))[:20]

    # Award / press mentions
    award_parts = []
    for tag in soup.find_all(True):
        attrs = " ".join([
            tag.get("id", ""),
            " ".join(tag.get("class", [])),
        ]).lower()
        if any(kw in attrs for kw in AWARD_KEYWORDS):
            text = _clean(tag.get_text())
            if len(text) > 20:
                award_parts.append(text[:300])
    award_press_text = " | ".join(award_parts[:5])

    # Fallback: general paragraph text
    all_p = " ".join(_clean(p.get_text()) for p in soup.find_all("p") if p.get_text().strip())
    all_text_excerpt = all_p[:3000]

    # Detect JS-heavy SPA with no content
    total_content = " ".join([title, meta_desc, about_text, all_text_excerpt])
    if len(total_content.strip()) < 80:
        raise ValueError(
            "Aucun contenu lisible trouvé. Ce site charge peut-être son contenu "
            "dynamiquement (JavaScript/React). L'analyse ne peut pas être effectuée."
        )

    return {
        "url": url,
        "title": title,
        "meta_description": meta_desc,
        "headings": headings,
        "about_text": about_text,
        "nav_links": nav_links,
        "award_press_text": award_press_text,
        "all_text_excerpt": all_text_excerpt,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GEMINI ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_SCORING_INSTRUCTIONS = """SCULPTURES NADÈGE MOUYSSINAT :
Sculptures contemporaines en pierre, marbre, béton ciré, résine.
Formes organiques épurées ou géométriques — surfaces texturées ou polies.
Palette exclusive : blanc, gris, beige, noir, taupe.
Pièces statement museum-quality (40 cm–1 m), prix 2 500–13 000 €.
Elles s'intègrent dans des espaces à forte respiration architecturale,
aux côtés d'un art sobre et structurant — pas décoratif.

═══ CRITÈRE 1 — LUXE (0 à 3 points) ═══
Évalue le niveau de positionnement marché du studio.

3 points — Ultra-premium :
  Clients explicites : milliardaires, familles royales, jets privés, yachts, palaces,
  hôtels ultra-luxe (Aman, Cheval Blanc, Rosewood niveau flagship).
  Tarifs ou projets manifestement dans le top 1% mondial.

1–2 points — Premium :
  Résidentiel haut de gamme (appartements/villas > 2M€ visibles),
  hôtellerie luxe standard, clientèle aisée confirmée.
  2 pts si clairement affirmé, 1 pt si probable mais ambigu.

0 point — Non premium :
  Marché accessible, projets commerciaux standard, aucun signal de luxe.

═══ CRITÈRE 2 — STYLE NADÈGE (0 à 2 points) ═══
IMPORTANT : Regarde les photos de projets et d'œuvres d'art présentes sur le site.
Pose-toi cette question : "Une sculpture en pierre sobre et organique de Nadège
trouverait-elle naturellement sa place dans ces espaces ou aux côtés de ces œuvres ?"
Tu NE compares PAS le style du site à un style abstrait — tu évalues la compatibilité
concrète entre les espaces/œuvres montrés et les sculptures de Nadège.

2 points — Forte compatibilité :
  Projets avec volumes clairs, matières nobles (marbre, béton, plâtre, bois brut),
  espaces épurés avec de la respiration autour des objets, palette neutre dominante.
  Art déjà présent sous forme de sculptures contemporaines sobres, pièces abstraites
  organiques, céramiques statement — ambiance "quiet luxury", raffinement discret.

1 point — Compatibilité partielle :
  Quelques projets compatibles mélangés à des styles plus chargés ou colorés.
  Style globalement élégant mais pas clairement aligné avec les sculptures de Nadège.

0 point — Incompatible :
  Intérieurs maximalistes, très colorés, baroques, très chargés en motifs.
  Art figuratif académique, pop art criard, peintures très colorées, décoratif grand public.
  Projets dominés par couleurs vives, patterns forts, ou ornements surchargés.

═══ CRITÈRE 3 — BONUS ART (0 ou 1 point) ═══
+1 si mention EXPLICITE sur le site d'un service d'intégration d'œuvres d'art :
"art advisory", "art sourcing", "sélection d'œuvres", "nous plaçons des œuvres
pour nos clients", "accompagnement artistique", "curation", ou équivalent.
0 si aucune mention explicite de ce type de service.

═══ CALCUL ═══
score_global = luxe_score + style_score + bonus_art
Si score_global > 5, plafonner à 5.

═══ RÈGLES ABSOLUES ═══
- luxe : entier strictement entre 0 et 3.
- style : entier strictement entre 0 et 2.
- bonus_art : strictement 0 ou 1.
- score_global = somme des trois, plafonné à 5, minimum 1.
- L'explication_globale indique EXPLICITEMENT les notes obtenues :
  "Luxe : X/3 — [raison courte]. Style Nadège : X/2 — [raison courte]. Bonus art : X/1."

Réponds UNIQUEMENT avec ce JSON (aucun texte avant ou après) :
{
  "score_global": <entier 1-5>,
  "explication_globale": "<Luxe : X/3 — raison. Style Nadège : X/2 — raison. Bonus art : X/1.>",
  "criteres": {
    "luxe":      { "score": <0-3>, "max": 3, "label": "Positionnement Luxe",  "explication": "<str>" },
    "style":     { "score": <0-2>, "max": 2, "label": "Style Nadège",         "explication": "<str>" },
    "bonus_art": { "score": <0|1>, "max": 1, "label": "Intégration d'Art",    "explication": "<str>" }
  }
}"""

# Mutable at runtime via /prompt — resets on service restart
_scoring_instructions = DEFAULT_SCORING_INSTRUCTIONS


def build_prompt(scraped: dict) -> str:
    headings_str = " | ".join(scraped["headings"][:12]) if scraped["headings"] else "—"
    nav_str = " | ".join(scraped["nav_links"][:10]) if scraped["nav_links"] else "—"

    site_section = f"""SITE ANALYSÉ : {scraped['url']}
TITRE : {scraped['title'] or '—'}
DESCRIPTION META : {scraped['meta_description'] or '—'}
TITRES DE SECTIONS (H1-H3) : {headings_str}
TEXTE ABOUT / PHILOSOPHIE : {scraped['about_text'][:600] or '—'}
NAVIGATION : {nav_str}
MENTIONS PRESSE / AWARDS : {scraped['award_press_text'][:400] or '—'}
EXTRAIT GÉNÉRAL : {scraped['all_text_excerpt'][:1500]}"""

    return f"""=== DONNÉES DU SITE À ANALYSER ===

{site_section}

=== INSTRUCTIONS D'ÉVALUATION ===

{_scoring_instructions}"""


def analyze_with_claude(scraped: dict) -> dict:
    prompt = build_prompt(scraped)

    try:
        response = cerebras.chat.completions.create(
            model="llama3.1-8b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        raw_text = response.choices[0].message.content.strip()
    except Exception as e:
        err = str(e).lower()
        if "api key" in err or "permission" in err or "unauthorized" in err or "authentication" in err:
            raise ValueError("Clé API invalide. Vérifiez CEREBRAS_API_KEY.")
        if "quota" in err or "rate" in err or "limit" in err:
            raise ValueError("Limite d'utilisation de l'API atteinte. Réessayez dans quelques secondes.")
        if "connection" in err or "unavailable" in err:
            raise ValueError("Erreur de connexion à l'API Cerebras.")
        raise ValueError(f"Erreur Cerebras : {str(e)}")

    # Strip markdown fences
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```[a-z]*\n?", "", raw_text)
        raw_text = re.sub(r"\n?```$", "", raw_text)

    # Try direct parse first, then extract first {...} block from response
    result = None
    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
            except json.JSONDecodeError:
                pass

    if result is None:
        raise ValueError("L'analyse a produit une réponse inattendue. Réessayez.")

    # Recalculate score_global from criteria to avoid AI arithmetic errors
    criteres = result.get("criteres", {})
    computed = sum(
        int(v.get("score", 0))
        for v in criteres.values()
        if isinstance(v, dict)
    )
    result["score_global"] = max(1, min(5, computed))
    return result


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    body = request.get_json(silent=True) or {}
    url = (body.get("url") or "").strip()

    if not url:
        return jsonify({"success": False, "error": "Veuillez entrer une URL."})

    # Auto-prepend https if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        scraped = scrape_website(url)
        result = analyze_with_claude(scraped)
        return jsonify({"success": True, "data": result, "url": url})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)})
    except Exception as e:
        app.logger.error("Unexpected error: %s", str(e))
        return jsonify({"success": False, "error": "Erreur inattendue lors de l'analyse."})


@app.route("/clay", methods=["POST"])
def clay_webhook():
    """
    Endpoint for Clay webhooks.
    Accepts: { "url": "https://studio-exemple.com" }
    Also accepts "website" or "domain" as field names.
    Returns: { "score_global": 4, "explication_globale": "..." }
    On error: { "score_global": null, "explication_globale": null, "error": "..." }
    """
    body = request.get_json(silent=True) or {}
    url = (body.get("url") or body.get("website") or body.get("domain") or "").strip()

    if not url:
        return jsonify({"score_global": None, "explication_globale": None, "error": "Champ url manquant."})

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        scraped = scrape_website(url)
        result = analyze_with_claude(scraped)
        return jsonify({
            "score_global": result.get("score_global"),
            "explication_globale": result.get("explication_globale"),
        })
    except ValueError as e:
        return jsonify({"score_global": None, "explication_globale": None, "error": str(e)})
    except Exception as e:
        app.logger.error("Clay webhook error: %s", str(e))
        return jsonify({"score_global": None, "explication_globale": None, "error": "Erreur inattendue."})


@app.route("/prompt", methods=["GET", "POST"])
def prompt_editor():
    global _scoring_instructions
    if request.method == "POST":
        new_instructions = (request.form.get("instructions") or "").strip()
        if new_instructions:
            _scoring_instructions = new_instructions
        return redirect("/prompt")
    return render_template(
        "prompt.html",
        instructions=_scoring_instructions,
        is_default=(_scoring_instructions == DEFAULT_SCORING_INSTRUCTIONS),
    )


@app.route("/prompt/reset", methods=["POST"])
def prompt_reset():
    global _scoring_instructions
    _scoring_instructions = DEFAULT_SCORING_INSTRUCTIONS
    return redirect("/prompt")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
