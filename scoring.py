"""
Reglas de puntuación (0-100) por área auditada.

IMPORTANTE — honestidad sobre qué es "en vivo" y qué es heurística:
  - Reseñas, fotos, categoría, teléfono/web/horario: vienen directo de Google Places API.
  - Palabras clave: el volumen es real (Keywords Everywhere); "¿se usa ya?" es una
    coincidencia de texto simple contra nombre/categoría/descripción del negocio.
  - Sitio web: hallazgos reales de auditoria_website() (peticion HTTP real al sitio).
  - Citas locales (Apple Maps, Waze, directorios...): NO se pueden verificar automáticamente
    sin contratar APIs adicionales de pago por cada directorio, así que esa sección se
    entrega como checklist manual editable (igual que en la plantilla de Word).

Estas fórmulas son un punto de partida razonable, no un estándar de la industria —
Ricardo puede ajustarlas libremente en este archivo.
"""


def score_reviews(rating, review_count):
    try:
        rating = float(rating)
    except (TypeError, ValueError):
        rating = 0
    try:
        review_count = int(review_count)
    except (TypeError, ValueError):
        review_count = 0

    count_score = min(review_count / 50, 1) * 60  # 50+ reseñas = puntos máximos por volumen
    rating_score = max((rating - 1) / 4, 0) * 40 if rating else 0  # 5.0 = 40 pts, 1.0 = 0 pts
    return round(count_score + rating_score)


def score_photos_posts(photo_count):
    try:
        photo_count = int(photo_count)
    except (TypeError, ValueError):
        photo_count = 0
    return round(min(photo_count / 20, 1) * 100)  # 20+ fotos = máximo


def score_profile_completeness(place):
    fields = ["website", "phone", "hours", "category"]
    present = sum(1 for f in fields if place.get(f) and place.get(f) != "—")
    base = (present / len(fields)) * 70
    photo_bonus = min(place.get("photoCount", 0) / 15, 1) * 30
    return round(base + photo_bonus)


def score_keywords(keywords_status):
    """keywords_status: lista de 'No se usa' / 'Parcial' / 'Optimizado'."""
    if not keywords_status:
        return 0
    weights = {"No se usa": 0, "Parcial": 0.5, "Optimizado": 1}
    total = sum(weights.get(s, 0) for s in keywords_status)
    return round((total / len(keywords_status)) * 100)


def score_website(website_findings):
    if not website_findings:
        return 50  # sin datos suficientes
    penalty = {"Crítico": 30, "Alto": 18, "Medio": 8, "Bajo": 2}
    score = 100
    for f in website_findings:
        score -= penalty.get(f["severity"], 5)
    return max(0, round(score))


def status_label(score):
    if score >= 80:
        return "Bueno"
    if score >= 60:
        return "Aceptable"
    if score >= 40:
        return "Necesita Trabajo"
    if score >= 20:
        return "Débil"
    return "Crítico"


def overall_status_label(score):
    if score >= 80:
        return "Bueno"
    if score >= 60:
        return "Aceptable"
    if score >= 35:
        return "Deficiente"
    return "Crítico"


def keyword_current_use(keyword, place):
    """Heurística simple: ¿el término aparece ya en nombre/categoría del negocio?
    No es un rank tracker real — solo evita marcar todo como 'No se usa' a ciegas."""
    haystack = " ".join([
        str(place.get("name", "")),
        str(place.get("category", "")),
        str(place.get("categoriesAdd", "")),
    ]).lower()
    kw = keyword.lower()
    words = [w for w in kw.split() if len(w) > 3]
    if not words:
        return "No se usa"
    matches = sum(1 for w in words if w in haystack)
    ratio = matches / len(words)
    if ratio >= 0.8:
        return "Optimizado"
    if ratio >= 0.3:
        return "Parcial"
    return "No se usa"
