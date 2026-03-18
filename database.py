"""
Base de données de référence — Studios de design d'intérieur
Catégories de 1 (peu prioritaire) à 5 (ultra pertinent)
"""

STUDIOS = [
    # ── CATÉGORIE 5 — ULTRA PERTINENT ─────────────────────────────────────
    {"name": "Nicole Hollis",               "country": "USA",           "category": 5},
    {"name": "Studio Shamshiri",            "country": "USA",           "category": 5},
    {"name": "Roman and Williams",          "country": "USA",           "category": 5},
    {"name": "Rose Uniacke",               "country": "UK",            "category": 5},
    {"name": "Pierre Yovanovitch",         "country": "France",        "category": 5},
    {"name": "Joseph Dirand Architecture", "country": "France",        "category": 5},
    {"name": "Liaigre",                    "country": "France",        "category": 5},
    {"name": "Axel Vervoordt",             "country": "Belgique",      "category": 5},
    {"name": "Banda",                      "country": "UK",            "category": 5},
    {"name": "Keller Behun",               "country": "USA",           "category": 5},
    {"name": "Studio Sofield",             "country": "USA",           "category": 5},
    {"name": "Gabellini Sheppard",         "country": "USA",           "category": 5},
    {"name": "Bryan O'Sullivan Studio",    "country": "UK",            "category": 5},
    {"name": "Studio Indigo",              "country": "UK",            "category": 5},
    {"name": "Dimorestudio",               "country": "Italie",        "category": 5},
    {"name": "Danielle Siggerud",          "country": "Danemark",      "category": 5},
    {"name": "Bernard Dubois Architects",  "country": "Belgique",      "category": 5},
    {"name": "Aline Asmar d'Amman",        "country": "France",        "category": 5},
    {"name": "Róisín Lafferty",            "country": "Irlande",       "category": 5},
    {"name": "Benoit Redard",              "country": "France",        "category": 5},
    {"name": "Atelier Hillier",            "country": "UK",            "category": 5},
    {"name": "Le Cann",                    "country": "France",        "category": 5},
    {"name": "Studio Paolo Ferrari",       "country": "Canada",        "category": 5},
    {"name": "Studio Liu",                 "country": "International", "category": 5},
    {"name": "Autoban",                    "country": "Turquie",       "category": 5},
    {"name": "Zeynep Fadillioglu Design",  "country": "Turquie",       "category": 5},
    {"name": "Jouin Manku",                "country": "France",        "category": 5},
    {"name": "Kevin Barry Art Advisory",   "country": "USA",           "category": 5},

    # ── CATÉGORIE 4 — TRÈS PERTINENT ──────────────────────────────────────
    {"name": "Ashe Leandro",               "country": "USA",           "category": 4},
    {"name": "Olson Kundig",               "country": "USA",           "category": 4},
    {"name": "Marmol Radziner",            "country": "USA",           "category": 4},
    {"name": "Wecselman Design",           "country": "USA",           "category": 4},
    {"name": "Thomas Pheasant",            "country": "USA",           "category": 4},
    {"name": "Suzanne Lovell Inc",         "country": "USA",           "category": 4},
    {"name": "Drake / Anderson",           "country": "USA",           "category": 4},
    {"name": "Elizabeth Krueger Design",   "country": "USA",           "category": 4},
    {"name": "Jessica Gersten Design",     "country": "USA",           "category": 4},
    {"name": "Karen Asprea Studio",        "country": "USA",           "category": 4},
    {"name": "Lucinda Loya Interiors",     "country": "USA",           "category": 4},
    {"name": "Studio KAO",                 "country": "UK",            "category": 4},
    {"name": "Natalia Miyar Atelier",      "country": "UK",            "category": 4},
    {"name": "Piero Lissoni",              "country": "Italie",        "category": 4},
    {"name": "Antonio Citterio Patricia Viel", "country": "Italie",   "category": 4},
    {"name": "Tristan Auer",               "country": "France",        "category": 4},
    {"name": "Jean-Philippe Nuel",         "country": "France",        "category": 4},
    {"name": "Humbert & Poyet",            "country": "France",        "category": 4},
    {"name": "Stephanie Coutas",           "country": "France",        "category": 4},
    {"name": "Olivier Lempereur",          "country": "France",        "category": 4},
    {"name": "Huma Sulaiman Design",       "country": "USA",           "category": 4},
    {"name": "Rinck",                      "country": "France",        "category": 4},
    {"name": "Moinard Bétaille",           "country": "France",        "category": 4},
    {"name": "Sybille de Margerie",        "country": "France",        "category": 4},
    {"name": "Oleg Klodt Design",          "country": "UK",            "category": 4},
    {"name": "Cristina Carulla Studio",    "country": "Espagne",       "category": 4},
    {"name": "XBD Collective",             "country": "International", "category": 4},
    {"name": "Bar Studio",                 "country": "Australie",     "category": 4},
    {"name": "Studio Volpe",               "country": "Italie",        "category": 4},
    {"name": "VI Architects",              "country": "International", "category": 4},
    {"name": "Kim Lambert Design",         "country": "USA",           "category": 4},
    {"name": "Studio PVG",                 "country": "International", "category": 4},
    {"name": "Daniel Schaefer Studio",     "country": "Allemagne",     "category": 4},
    {"name": "Bernd Gruber Interior",      "country": "Autriche",      "category": 4},
    {"name": "Regis Botta",                "country": "France",        "category": 4},
    {"name": "Berg Interior",              "country": "International", "category": 4},
    {"name": "Sarah Nicollier Interiors",  "country": "Suisse",        "category": 4},
    {"name": "Anne Carr Design",           "country": "USA",           "category": 4},
    {"name": "Nora Chou",                  "country": "International", "category": 4},
    {"name": "Karnalli Design",            "country": "International", "category": 4},
    {"name": "Galli Studio",               "country": "Italie",        "category": 4},
    {"name": "Fischer Mordrelle",          "country": "France",        "category": 4},
    {"name": "LBM Architecture",           "country": "France",        "category": 4},
    {"name": "Maison Numero 20",           "country": "France",        "category": 4},
    {"name": "Diff Studio",                "country": "International", "category": 4},
    {"name": "Ines Deschodt",              "country": "Belgique",      "category": 4},
    {"name": "Widell Boschetti",           "country": "USA",           "category": 4},
    {"name": "Zuretti Design",             "country": "France",        "category": 4},
    {"name": "Sarsen Interiors",           "country": "UK",            "category": 4},
    {"name": "Giuseppe Bavuso Design",     "country": "Italie",        "category": 4},
    {"name": "Agence Kuentz Legall",       "country": "France",        "category": 4},
    {"name": "Studio 1872",                "country": "International", "category": 4},

    # ── CATÉGORIE 3 — PERTINENT ────────────────────────────────────────────
    {"name": "Lawson Robb",                "country": "UK",            "category": 3},
    {"name": "Elicyon",                    "country": "UK",            "category": 3},
    {"name": "Taylor Howes",               "country": "UK",            "category": 3},
    {"name": "Rigby & Rigby",              "country": "UK",            "category": 3},
    {"name": "Martin Hulbert Design",      "country": "UK",            "category": 3},
    {"name": "Studio Shields",             "country": "Australie",     "category": 3},
    {"name": "Katie Watkinson Interiors",  "country": "UK",            "category": 3},
    {"name": "Hill House Interiors",       "country": "UK",            "category": 3},
    {"name": "Lindsey Goddard Interiors",  "country": "USA",           "category": 3},
    {"name": "Rachael Lauren Interiors",   "country": "USA",           "category": 3},
    {"name": "Bettencourt Manor",          "country": "UK",            "category": 3},
    {"name": "Josephine Fossey",           "country": "UK",            "category": 3},
    {"name": "Siriano Interiors",          "country": "International", "category": 3},
    {"name": "Fawn Galli Interiors",       "country": "USA",           "category": 3},
    {"name": "Nicole Fuller Interiors",    "country": "USA",           "category": 3},
    {"name": "Jamee Lynn Design",          "country": "USA",           "category": 3},
    {"name": "Evento Designs",             "country": "UAE",           "category": 3},
    {"name": "Volu Studios",               "country": "International", "category": 3},
    {"name": "Cartelle Design",            "country": "USA",           "category": 3},
    {"name": "Ariana Ahmad Design",        "country": "International", "category": 3},
    {"name": "Benny Benlolo",              "country": "UK",            "category": 3},
    {"name": "Fleur de Lesalle",           "country": "France",        "category": 3},
    {"name": "Marso Studio",               "country": "Italie",        "category": 3},
    {"name": "Belousova Interior",         "country": "Ukraine",       "category": 3},
    {"name": "Garce Dimofski",             "country": "Macédoine",     "category": 3},
    {"name": "Nuova Home",                 "country": "Italie",        "category": 3},
    {"name": "Crina Architecture",         "country": "Roumanie",      "category": 3},
    {"name": "Bo Ya Design",               "country": "International", "category": 3},
    {"name": "Tanju Özelgin",              "country": "Turquie",       "category": 3},
    {"name": "Rabih Hage Studio",          "country": "UK",            "category": 3},
    {"name": "Galal Mahmoud Architects",   "country": "Égypte",        "category": 3},
    {"name": "Mann Coatanea",              "country": "France",        "category": 3},
    {"name": "Durbiano Architecture",      "country": "France",        "category": 3},
    {"name": "Flamine Architecture",       "country": "France",        "category": 3},
    {"name": "Yodezeen Architects",        "country": "Ukraine",       "category": 3},
    {"name": "Luxoria Interiors",          "country": "UAE",           "category": 3},
    {"name": "Antes Architecture",         "country": "Espagne",       "category": 3},
    {"name": "Chused & Co",                "country": "International", "category": 3},
    {"name": "El Hussieni",                "country": "International", "category": 3},
    {"name": "Nkey Architects",            "country": "Ukraine",       "category": 3},
    {"name": "Hirsch Bedner Associates",   "country": "International", "category": 3},
    {"name": "CCD Cheng Chung Design",     "country": "Hong Kong",     "category": 3},
    {"name": "Dseesion Interiors",         "country": "International", "category": 3},

    # ── CATÉGORIE 2 — SECONDAIRE MAIS À GARDER ────────────────────────────
    {"name": "AEA Interiors",              "country": "International", "category": 2},
    {"name": "Studio Emblem",              "country": "International", "category": 2},
    {"name": "Bridges Brown Interiors",    "country": "USA",           "category": 2},
    {"name": "Catch Design Studio",        "country": "International", "category": 2},
    {"name": "Loak Designs",               "country": "International", "category": 2},
    {"name": "Asthetique Group",           "country": "International", "category": 2},
    {"name": "Diachok Architects",         "country": "Ukraine",       "category": 2},
    {"name": "Architecture Interior UE",   "country": "International", "category": 2},
    {"name": "Tarras Design House",        "country": "International", "category": 2},
    {"name": "Brahman Perera",             "country": "Australie",     "category": 2},
    {"name": "Caprini Pellerin",           "country": "France",        "category": 2},
    {"name": "Masoor Studio",              "country": "International", "category": 2},
    {"name": "Alena Pautova",              "country": "Russie",        "category": 2},
    {"name": "Imperium UAE",               "country": "UAE",           "category": 2},
    {"name": "Gatserelia Design",          "country": "International", "category": 2},
    {"name": "Bozhinovski Design",         "country": "Macédoine",     "category": 2},
    {"name": "LMD Design Studio",          "country": "Norvège",       "category": 2},
    {"name": "Julie Interiors",            "country": "International", "category": 2},
    {"name": "Studio One Designs",         "country": "International", "category": 2},
    {"name": "Helena Clunies Ross",        "country": "UK",            "category": 2},
    {"name": "MBDS",                       "country": "International", "category": 2},
    {"name": "Mdezeiner",                  "country": "International", "category": 2},
    {"name": "M Interior SA",              "country": "Arabie Saoudite","category": 2},
    {"name": "Dida Home",                  "country": "Italie",        "category": 2},
    {"name": "Rock and Villa",             "country": "International", "category": 2},
    {"name": "Quintana Partners",          "country": "International", "category": 2},
    {"name": "Lexi Zavad Interiors",       "country": "International", "category": 2},
    {"name": "Ivan Ogienko Company",       "country": "UAE",           "category": 2},
    {"name": "Allon Verhees",              "country": "Pays-Bas",      "category": 2},

    # ── CATÉGORIE 1 — PEU PRIORITAIRE ─────────────────────────────────────
    {"name": "Martin Kemp Design",         "country": "UK",            "category": 1},
    {"name": "Chris C. Shao",              "country": "International", "category": 1},
    {"name": "Vandervelpen",               "country": "Belgique",      "category": 1},
    {"name": "Atelier Daaa",               "country": "France",        "category": 1},
    {"name": "Commune Design",             "country": "USA",           "category": 1},
]


CATEGORY_DESCRIPTIONS = {
    5: (
        "ULTRA PERTINENT — Studios de référence mondiale en design résidentiel de très "
        "grand luxe. Clientèle UHNW (Ultra High Net Worth). Réputation internationale, "
        "projets iconiques, présence éditoriale forte (AD, Vogue, T Magazine…). "
        "Esthétique soignée, espaces épurés ou sculpturaux, art intégré."
    ),
    4: (
        "TRÈS PERTINENT — Positionnement premium confirmé. Mix résidentiel luxe et "
        "hospitality haut de gamme (palaces, yachts, avions privés). Réputation solide "
        "dans leur marché, clientèle aisée, portfolio de qualité."
    ),
    3: (
        "PERTINENT — Qualité professionnelle confirmée, positionnement mid-to-high. "
        "Projets résidentiels de standing ou hospitality premium. Présence éditoriale "
        "correcte, clientèle upper-middle."
    ),
    2: (
        "SECONDAIRE MAIS À GARDER — Studios commerciaux généralistes ou résidentiel "
        "standard avec quelques projets premium. Peu de présence éditoriale luxe. "
        "À surveiller mais pas prioritaires."
    ),
    1: (
        "PEU PRIORITAIRE — Commercial mass-market, résidentiel standard, ou esthétique "
        "peu alignée. Faible potentiel de synergie à court terme."
    ),
}


def get_examples_by_category(n: int = 8) -> dict:
    """Retourne n exemples par catégorie (1-5), utilisés pour construire le prompt Claude."""
    result = {}
    for cat in range(1, 6):
        names = [s["name"] for s in STUDIOS if s["category"] == cat]
        result[cat] = names[:n]
    return result


def get_category_descriptions() -> dict:
    return CATEGORY_DESCRIPTIONS
