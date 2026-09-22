"""
Integraciones con datos reales:

  - Google Places API (New)  -> ficha del negocio + competidores en Google Maps
  - Keywords Everywhere API  -> volumen de búsqueda mensual por palabra clave
  - Auditor de sitio web en vivo -> checks técnicos de SEO local (sin API de pago)

Cada función regresa (resultado, error). Si error no es None, resultado puede
venir incompleto o vacío — la app decide cómo mostrarlo al usuario.
"""

import re
import requests

PLACES_BASE = "https://places.googleapis.com/v1/places"
KWE_URL = "https://api.keywordseverywhere.com/v1/get_keyword_data"

DEFAULT_TIMEOUT = 12


# ---------------------------------------------------------------------------
# Google Places API (New)
# ---------------------------------------------------------------------------

PLACE_DETAIL_FIELDS = ",".join([
    "id", "displayName", "formattedAddress", "internationalPhoneNumber",
    "nationalPhoneNumber", "websiteUri", "rating", "userRatingCount",
    "primaryTypeDisplayName", "types", "businessStatus", "regularOpeningHours",
    "photos", "editorialSummary", "reviews",
])

SEARCH_FIELDS = ",".join([
    "places.id", "places.displayName", "places.formattedAddress",
    "places.rating", "places.userRatingCount", "places.websiteUri",
    "places.primaryTypeDisplayName",
])


def find_place(api_key, query, region_code="mx", language_code="es"):
    """Busca un negocio por texto libre (nombre + ciudad) y regresa el primer resultado."""
    try:
        resp = requests.post(
            f"{PLACES_BASE}:searchText",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": SEARCH_FIELDS,
            },
            json={"textQuery": query, "regionCode": region_code, "languageCode": language_code},
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        places = resp.json().get("places", [])
        if not places:
            return None, "No se encontró ningún negocio con esa búsqueda en Google Maps."
        return places[0], None
    except requests.exceptions.RequestException as e:
        return None, f"Error consultando Google Places (búsqueda): {e}"


def get_place_details(api_key, place_id, language_code="es"):
    try:
        resp = requests.get(
            f"{PLACES_BASE}/{place_id}",
            headers={
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": PLACE_DETAIL_FIELDS,
            },
            params={"languageCode": language_code},
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Error consultando Google Places (detalle): {e}"


def search_competitors(api_key, niche_query, region_code="mx", language_code="es", max_results=6):
    """Busca 'niche_query' (p.ej. 'aire acondicionado en Zapopan') y regresa una lista
    de negocios que Google Maps posiciona hoy para ese término."""
    try:
        resp = requests.post(
            f"{PLACES_BASE}:searchText",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": SEARCH_FIELDS,
            },
            json={"textQuery": niche_query, "regionCode": region_code, "languageCode": language_code},
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        places = resp.json().get("places", [])[:max_results]
        out = []
        for p in places:
            out.append({
                "name": p.get("displayName", {}).get("text", "—"),
                "rating": p.get("rating", "—"),
                "reviewCount": p.get("userRatingCount", "—"),
                "website": p.get("websiteUri", "—"),
            })
        return out, None
    except requests.exceptions.RequestException as e:
        return [], f"Error buscando competidores: {e}"


def normalize_place(details):
    """Convierte la respuesta cruda de Place Details al shape que usa report_generator."""
    hours = "—"
    oh = details.get("regularOpeningHours")
    if oh and oh.get("weekdayDescriptions"):
        hours = " | ".join(oh["weekdayDescriptions"][:2]) + (" ..." if len(oh["weekdayDescriptions"]) > 2 else "")

    types = details.get("types", [])
    primary = details.get("primaryTypeDisplayName", {}).get("text") if isinstance(details.get("primaryTypeDisplayName"), dict) else None

    return {
        "place_id": details.get("id"),
        "name": details.get("displayName", {}).get("text", "—"),
        "website": details.get("websiteUri", "—"),
        "phone": details.get("nationalPhoneNumber") or details.get("internationalPhoneNumber") or "—",
        "address": details.get("formattedAddress", "—"),
        "category": primary or (types[0].replace("_", " ").title() if types else "—"),
        "categoriesAdd": ", ".join(t.replace("_", " ").title() for t in types[1:6]) if len(types) > 1 else "—",
        "rating": details.get("rating", "—"),
        "reviewCount": details.get("userRatingCount", 0),
        "hours": hours,
        "photoCount": len(details.get("photos", [])),
        "businessStatus": details.get("businessStatus", "—"),
        "reviews": details.get("reviews", []),
    }


# ---------------------------------------------------------------------------
# Keywords Everywhere
# ---------------------------------------------------------------------------

# Códigos de país que usa Keywords Everywhere (num). 2484 = México.
COUNTRY_CODES = {"mx": 2484, "us": 2840, "es": 2724, "co": 2170, "ar": 2032, "cl": 2152, "pe": 2604}


def get_keyword_volumes(api_key, keywords, country="mx", currency="MXN"):
    """Regresa lista de dicts {keyword, volume, competition, cpc} usando Keywords Everywhere.
    Si falla, regresa (None, mensaje_error) para que la app pueda avisar y seguir sin estos datos."""
    if not keywords:
        return [], None
    try:
        resp = requests.post(
            KWE_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            data={
                "country": country,
                "currency": currency,
                "dataSource": "gkp",
                "kw[]": keywords,
            },
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("credits_consumed", 1) == 0 and not payload.get("data"):
            return None, "Keywords Everywhere no regresó datos (¿saldo de créditos agotado?)."
        rows = payload.get("data", [])
        out = []
        by_kw = {r.get("keyword", "").lower(): r for r in rows}
        for kw in keywords:
            r = by_kw.get(kw.lower(), {})
            vol = r.get("vol")
            comp = r.get("competition")
            out.append({
                "keyword": kw,
                "volume": f"{vol:,}/mes" if isinstance(vol, (int, float)) else "—",
                "competition": _competition_label(comp),
                "cpc": r.get("cpc", {}).get("value") if isinstance(r.get("cpc"), dict) else None,
            })
        return out, None
    except requests.exceptions.RequestException as e:
        return None, f"Error consultando Keywords Everywhere: {e}"


def _competition_label(comp):
    if comp is None:
        return "—"
    try:
        c = float(comp)
    except (TypeError, ValueError):
        return "—"
    if c >= 0.66:
        return "Alta"
    if c >= 0.33:
        return "Media"
    return "Baja"


# ---------------------------------------------------------------------------
# Auditor de sitio web en vivo (sin API de pago — solo requests + regex simples)
# ---------------------------------------------------------------------------

def audit_website(url):
    """Descarga la portada del sitio y revisa señales básicas de SEO local técnico.
    Regresa (lista_de_hallazgos, error)."""
    if not url or url in ("—", ""):
        return [], "No se proporcionó sitio web para auditar."
    if not url.startswith("http"):
        url = "https://" + url

    findings = []
    try:
        resp = requests.get(url, timeout=DEFAULT_TIMEOUT, headers={"User-Agent": "Mozilla/5.0 (auditoria-gbp-bot)"})
        html = resp.text
    except requests.exceptions.RequestException as e:
        return [], f"No se pudo descargar el sitio ({e}). Verifica manualmente."

    n = 1

    # 1. Título
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if not title_match or not title_match.group(1).strip():
        findings.append({"num": n, "issue": "Sin título (title tag)", "details": "No se encontró una etiqueta <title> con contenido en la portada.", "severity": "Crítico"})
    elif len(title_match.group(1).strip()) < 15:
        findings.append({"num": n, "issue": "Título demasiado corto", "details": f"El título actual es \"{title_match.group(1).strip()}\" — no incluye suficiente contexto de servicio/ciudad.", "severity": "Medio"})
    n += 1

    # 2. Meta descripción
    meta_match = re.search(r'<meta[^>]+name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    if not meta_match or not meta_match.group(1).strip():
        findings.append({"num": n, "issue": "Sin metadescripción", "details": "No se encontró <meta name=\"description\"> en la portada.", "severity": "Alto"})
    n += 1

    # 3. H1
    h1_matches = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    if not h1_matches:
        findings.append({"num": n, "issue": "Sin encabezado H1", "details": "No hay ningún <h1> rastreable en el HTML crudo de la portada.", "severity": "Alto"})
    n += 1

    # 4. Datos estructurados (schema.org LocalBusiness)
    if "application/ld+json" not in html and "schema.org" not in html:
        findings.append({"num": n, "issue": "Sin datos estructurados (schema)", "details": "No se detectó marcado JSON-LD ni referencias a schema.org — falta LocalBusiness schema.", "severity": "Alto"})
    n += 1

    # 5. Texto visible mínimo (heurística de sitio renderizado solo con JS)
    visible_text = re.sub(r"<script.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    visible_text = re.sub(r"<style.*?</style>", " ", visible_text, flags=re.DOTALL | re.IGNORECASE)
    visible_text = re.sub(r"<[^>]+>", " ", visible_text)
    visible_text = re.sub(r"\s+", " ", visible_text).strip()
    if len(visible_text) < 200:
        findings.append({"num": n, "issue": "Posible renderizado solo con JavaScript", "details": f"Solo se detectaron ~{len(visible_text)} caracteres de texto visible en el HTML crudo — los rastreadores podrían ver una página casi en blanco.", "severity": "Crítico"})
    n += 1

    # 6. HTTPS
    if not url.startswith("https"):
        findings.append({"num": n, "issue": "Sitio sin HTTPS", "details": "El sitio no fuerza una conexión segura (HTTPS), lo que afecta confianza y SEO.", "severity": "Medio"})
    n += 1

    # 7. Teléfono/NAP visible en el HTML
    phone_pattern = re.search(r"(\+?\d[\d\s\-\(\)]{7,}\d)", visible_text)
    if not phone_pattern:
        findings.append({"num": n, "issue": "Sin teléfono visible en el HTML", "details": "No se detectó un número telefónico en el texto visible de la portada.", "severity": "Medio"})
    n += 1

    if not findings:
        findings.append({"num": 1, "issue": "Sin hallazgos críticos automáticos", "details": "Las revisiones automáticas básicas no encontraron problemas — se recomienda una revisión manual más profunda.", "severity": "Bajo"})

    return findings, None
