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
from flask import Flask, jsonify, render_template, request

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

NADEGE_REFERENCE = """
Nadège Mouyssinat est sculptrice contemporaine. Ses œuvres :
- Matériaux : pierre, marbre, béton ciré, résine — tons neutres (blanc, gris, noir, beige)
- Formes : organiques ou géométriques épurées, minimalistes, "statement pieces" museum-quality
- Prix : 2 500 € à 13 000 €
- Espaces adaptés : résidentiel luxe contemporain, hôtellerie boutique haut de gamme,
  galeries d'art, bureaux de direction, espaces épurés à volumes purs
- Espaces inadaptés : intérieurs baroques/maximalistes/très chargés, commerces grand public

Style Nadège côté design d'intérieur : palette neutre, lignes nettes, volumes purs, luxe discret.
Style Nadège côté art : sculpture contemporaine sobre, pas de peinture figurative académique,
pas d'art très coloré ou décoratif grand public.
"""


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

    instructions = f"""RÉFÉRENCE — ŒUVRES DE NADÈGE MOUYSSINAT :
{NADEGE_REFERENCE}

INSTRUCTION : Évalue ce site selon 5 critères binaires. Chaque critère vaut exactement 1 si validé,
0 sinon. Le score_global est la somme des 5 critères (entier de 0 à 5).

━━━ CRITÈRES ━━━

1. secteur_pertinent (+1)
   Le site appartient à un cabinet d'architecte d'intérieur, un studio de design d'intérieur,
   ou un consultant / galeriste en art destiné aux particuliers ou à l'hôtellerie.
   → Score 0 si : architecte d'extérieur pur, agence immobilière, décorateur grand public,
     agence de communication, autre secteur non lié au design intérieur ou à l'art.

2. segment_premium (+1)
   L'entreprise se positionne explicitement ou implicitement dans le segment premium
   ou ultra-premium : résidentiel de luxe, hôtellerie haut de gamme, yacht, jet privé,
   clientèle fortunée (UHNWI), tarifs ou projets manifestement élevés.
   → Score 0 si : marché grand public, prix accessibles, projets commerciaux standard.

3. style_nadege (+1)
   Le portfolio ou les réalisations présentées montrent une esthétique cohérente avec
   les sculptures de Nadège : intérieurs modernes, minimalistes, épurés, palette neutre
   (blanc/gris/beige/noir), volumes purs, luxe discret.
   Pour les consultants en art : les œuvres présentées sont contemporaines et sobres
   (sculpture, abstrait épuré) — pas de peinture figurative académique, pas d'art
   très coloré ou maximaliste.
   → Score 0 si : style baroque, maximaliste, très coloré, ou très chargé.

4. integration_art (+1)
   Le studio ou consultant intègre déjà des œuvres d'art dans ses projets :
   photos d'intérieurs avec sculptures ou œuvres d'art visibles dans le portfolio,
   section dédiée à l'art dans la navigation, collaboration mentionnée avec des artistes
   ou galeries, ou mise en avant de pièces artistiques dans leur communication.
   → Score 0 si : aucune trace d'art dans les projets présentés.

5. recherche_oeuvres (+1)
   Mention explicite d'une activité de recherche, sourcing ou prescription d'œuvres d'art
   pour les clients : "art advisory", "art sourcing", "sélection d'œuvres", "nous trouvons
   des œuvres pour nos clients", "accompagnement artistique", "curation", ou équivalent.
   → Score 0 si : aucune mention de ce type de service.

━━━ RÈGLES ABSOLUES ━━━
- Chaque score de critère est STRICTEMENT 0 ou 1 (pas de 0.5, pas d'autre valeur).
- score_global = somme exacte des 5 scores critères.
- L'explication de chaque critère commence par le verdict : "+1 →" ou "0 →" puis la raison.
- L'explication_globale mentionne les points validés et les manques clés.

Réponds UNIQUEMENT avec ce JSON (aucun texte avant ou après) :
{{
  "score_global": <entier 0-5>,
  "explication_globale": "<2-3 phrases de synthèse en français>",
  "criteres": {{
    "secteur_pertinent":  {{ "score": <0 ou 1>, "label": "Secteur Pertinent",    "explication": "<str>" }},
    "segment_premium":    {{ "score": <0 ou 1>, "label": "Segment Premium",       "explication": "<str>" }},
    "style_nadege":       {{ "score": <0 ou 1>, "label": "Style Nadège",          "explication": "<str>" }},
    "integration_art":    {{ "score": <0 ou 1>, "label": "Intégration d'Art",     "explication": "<str>" }},
    "recherche_oeuvres":  {{ "score": <0 ou 1>, "label": "Recherche d'Œuvres",   "explication": "<str>" }}
  }}
}}"""

    return f"""=== DONNÉES DU SITE À ANALYSER ===

{site_section}

=== INSTRUCTIONS D'ÉVALUATION ===

{instructions}"""


def analyze_with_claude(scraped: dict) -> dict:
    prompt = build_prompt(scraped)

    try:
        response = cerebras.chat.completions.create(
            model="llama-3.3-70b",
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

    # Strip any accidental markdown fences
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```[a-z]*\n?", "", raw_text)
        raw_text = re.sub(r"\n?```$", "", raw_text)

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        raise ValueError("L'analyse a produit une réponse inattendue. Réessayez.")

    result["score_global"] = max(1, min(5, result.get("score_global", 1)))
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


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
