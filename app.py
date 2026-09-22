"""
App de Streamlit: Auditoría GBP + SEO Local + Reputación (con datos en vivo).

Flujo:
  1. Capturas el negocio a auditar y buscas su ficha real en Google Maps.
  2. Buscas competidores reales para el nicho/ciudad.
  3. Pegas las palabras clave objetivo y obtienes volumen de búsqueda real.
  4. Auditas el sitio web en vivo (checks técnicos básicos).
  5. Generas el .docx con el mismo diseño de marca, listo para enviar.

Cómo correrla:
    pip install -r requirements.txt
    streamlit run app.py

Las API keys se leen de `st.secrets` (recomendado para producción / Streamlit Cloud)
o, si no existen, se piden en la barra lateral para pruebas locales rápidas.
"""

import datetime
import io

import streamlit as st

import integrations
import scoring
from universal_content import UNIVERSAL, DEFAULT_PREPARED_BY
from report_generator import build_report

st.set_page_config(page_title="Auditoría GBP · Reputación Digital", page_icon="📍", layout="wide")


def get_secret_or_input(key, label, sidebar):
    val = None
    try:
        val = st.secrets.get(key)
    except Exception:
        val = None
    if val:
        return val
    return sidebar.text_input(label, type="password", key=f"input_{key}")


# ---------------------------------------------------------------------------
# Sidebar: API keys y datos de quien prepara el reporte
# ---------------------------------------------------------------------------
st.sidebar.header("🔑 Conexiones")
places_key = get_secret_or_input("GOOGLE_PLACES_API_KEY", "Google Places API key", st.sidebar)
kwe_key = get_secret_or_input("KEYWORDS_EVERYWHERE_API_KEY", "Keywords Everywhere API key", st.sidebar)
st.sidebar.caption("Las keys nunca se guardan en el navegador del cliente — solo viven en esta sesión / en tus secrets.")

st.sidebar.header("🧑‍💼 Preparado por")
prep_name = st.sidebar.text_input("Nombre", value=DEFAULT_PREPARED_BY["name"])
prep_title = st.sidebar.text_input("Título", value=DEFAULT_PREPARED_BY["title"])
prep_contact = st.sidebar.text_input("Contacto", value=DEFAULT_PREPARED_BY["contact"])

st.title("📍 Auditoría GBP, SEO Local y Reputación — generador con datos reales")
st.caption("Llena los datos del prospecto, trae la información en vivo de Google y genera el reporte en Word con un clic.")

for key, default in [
    ("place_raw", None), ("place", None), ("competitors", []),
    ("keyword_rows", []), ("website_findings", []), ("website_error", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------------------------------------------------------
# 1. Negocio a auditar
# ---------------------------------------------------------------------------
st.subheader("1. Negocio a auditar")
col1, col2 = st.columns([2, 1])
with col1:
    business_query = st.text_input(
        "Nombre del negocio + ciudad (como lo buscarías en Google Maps)",
        placeholder="Ej. Climas del Valle aire acondicionado Zapopan",
    )
with col2:
    region_code = st.selectbox("País", ["mx", "us", "es", "co", "ar", "cl", "pe"], index=0)

if st.button("🔍 Buscar en Google Maps", type="primary", disabled=not places_key):
    if not business_query:
        st.warning("Escribe el nombre del negocio y la ciudad primero.")
    else:
        with st.spinner("Consultando Google Places..."):
            found, err = integrations.find_place(places_key, business_query, region_code=region_code)
            if err:
                st.error(err)
            else:
                details, err2 = integrations.get_place_details(places_key, found["id"])
                if err2:
                    st.error(err2)
                else:
                    st.session_state.place_raw = details
                    st.session_state.place = integrations.normalize_place(details)
                    st.success(f"Encontrado: {st.session_state.place['name']}")

if not places_key:
    st.info("Pon tu Google Places API key en la barra lateral para buscar negocios reales.")

place = st.session_state.place
if place:
    with st.expander("✅ Ficha encontrada en Google Maps (puedes ajustar cualquier campo antes de generar el reporte)", expanded=True):
        c1, c2 = st.columns(2)
        place["name"] = c1.text_input("Nombre del negocio", value=place["name"])
        place["website"] = c2.text_input("Sitio web", value=place["website"])
        place["phone"] = c1.text_input("Teléfono", value=place["phone"])
        place["address"] = c2.text_input("Dirección", value=place["address"])
        place["category"] = c1.text_input("Categoría principal", value=place["category"])
        place["categoriesAdd"] = c2.text_input("Categorías adicionales", value=place["categoriesAdd"])
        c3, c4, c5 = st.columns(3)
        place["rating"] = c3.number_input("Calificación", value=float(place["rating"]) if place["rating"] not in ("—", None) else 0.0, step=0.1, format="%.1f")
        place["reviewCount"] = c4.number_input("# Reseñas", value=int(place["reviewCount"] or 0), step=1)
        place["photoCount"] = c5.number_input("# Fotos (Google)", value=int(place["photoCount"] or 0), step=1)
        place["hours"] = st.text_input("Horario", value=place["hours"])

# ---------------------------------------------------------------------------
# 2. Competencia
# ---------------------------------------------------------------------------
st.subheader("2. Competencia en Google Maps")
niche_query = st.text_input(
    "Término de búsqueda del nicho (lo que un cliente escribiría)",
    placeholder="Ej. aire acondicionado en Zapopan",
)
if st.button("🔍 Buscar competidores reales", disabled=not places_key):
    if not niche_query:
        st.warning("Escribe el término de búsqueda del nicho primero.")
    else:
        with st.spinner("Consultando competidores en Google Maps..."):
            comps, err = integrations.search_competitors(places_key, niche_query, region_code=region_code)
            if err:
                st.error(err)
            st.session_state.competitors = comps
            if comps:
                st.success(f"Se encontraron {len(comps)} negocios posicionados para ese término.")

if st.session_state.competitors:
    st.dataframe(st.session_state.competitors, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# 3. Palabras clave
# ---------------------------------------------------------------------------
st.subheader("3. Palabras clave objetivo")
kw_text = st.text_area(
    "Una palabra clave por línea",
    placeholder="aire acondicionado Zapopan\nreparación de aire acondicionado Guadalajara\nrecarga de gas refrigerante Guadalajara",
    height=100,
)
kw_country = st.selectbox("País para volumen de búsqueda", list(integrations.COUNTRY_CODES.keys()), index=0)
if st.button("📊 Obtener volumen de búsqueda real", disabled=not kwe_key):
    keywords = [k.strip() for k in kw_text.splitlines() if k.strip()]
    if not keywords:
        st.warning("Pega al menos una palabra clave.")
    else:
        with st.spinner("Consultando Keywords Everywhere..."):
            rows, err = integrations.get_keyword_volumes(kwe_key, keywords, country=kw_country)
            if err:
                st.error(err)
            if rows:
                if place:
                    for r in rows:
                        r["currentUse"] = scoring.keyword_current_use(r["keyword"], place)
                        r["difficulty"] = r["competition"]
                st.session_state.keyword_rows = rows

if st.session_state.keyword_rows:
    st.dataframe(st.session_state.keyword_rows, use_container_width=True, hide_index=True)

if not kwe_key:
    st.info("Pon tu Keywords Everywhere API key en la barra lateral para traer volúmenes reales.")

# ---------------------------------------------------------------------------
# 4. Auditoría del sitio web
# ---------------------------------------------------------------------------
st.subheader("4. Auditoría técnica del sitio web (en vivo)")
if st.button("🌐 Auditar sitio web"):
    site = place["website"] if place and place.get("website") not in (None, "—") else None
    if not site:
        st.warning("No hay sitio web capturado. Búscalo primero en el paso 1 o edítalo manualmente ahí.")
    else:
        with st.spinner(f"Descargando y revisando {site}..."):
            findings, err = integrations.audit_website(site)
            st.session_state.website_findings = findings
            st.session_state.website_error = err
            if err:
                st.error(err)
            else:
                st.success(f"Se revisó {site} — {len(findings)} hallazgos.")

if st.session_state.website_findings:
    st.dataframe(st.session_state.website_findings, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# 5. Paquetes de inversión (editable, precargado)
# ---------------------------------------------------------------------------
st.subheader("5. Paquetes de inversión")
packages = []
default_packages = UNIVERSAL["packages"]
cols = st.columns(3)
for i, pkg in enumerate(default_packages):
    with cols[i]:
        st.markdown(f"**{pkg['name']}**")
        price = st.text_input(f"Precio — {pkg['name']}", value=pkg["price"], key=f"price_{i}")
        packages.append({**pkg, "price": price})

# ---------------------------------------------------------------------------
# 6. Generar reporte
# ---------------------------------------------------------------------------
st.subheader("6. Generar reporte")

citations_default = [
    {"platform": "Apple Maps (Business Connect)", "type": "Mapa", "status": "Verificar", "action": "Reclamar y agregar NAP, horario y fotos", "priority": "Crítico"},
    {"platform": "Bing Places", "type": "Mapa", "status": "Verificar", "action": "Importar desde GBP y verificar", "priority": "Alto"},
    {"platform": "Waze", "type": "Mapa / Navegación", "status": "Verificar", "action": "Agregar pin con categoría correcta", "priority": "Alto"},
    {"platform": "Facebook", "type": "Social", "status": "Verificar", "action": "Vincular NAP y conectar con GBP", "priority": "Alto"},
    {"platform": "Instagram", "type": "Social", "status": "Verificar", "action": "Crear portafolio de trabajos", "priority": "Medio"},
    {"platform": "Directorio local del nicho", "type": "Directorio", "status": "Verificar", "action": "Enviar ficha con NAP consistente", "priority": "Medio"},
    {"platform": "Sitio Web (NAP + Mapa)", "type": "Propio", "status": "Verificar", "action": "Agregar NAP rastreable, mapa embebido y schema", "priority": "Crítico"},
]
st.caption("Las citas locales (directorios) no se pueden verificar automáticamente sin contratar una API extra por cada plataforma — este checklist queda editable en el Word final.")

can_generate = place is not None
if not can_generate:
    st.warning("Busca el negocio en el paso 1 antes de generar el reporte.")

if st.button("📄 Generar reporte Word", type="primary", disabled=not can_generate):
    with st.spinner("Armando el documento..."):
        review_score = scoring.score_reviews(place["rating"], place["reviewCount"])
        photo_score = scoring.score_photos_posts(place["photoCount"])
        profile_score = scoring.score_profile_completeness(place)
        kw_statuses = [r["currentUse"] for r in st.session_state.keyword_rows] if st.session_state.keyword_rows else []
        kw_score = scoring.score_keywords(kw_statuses) if kw_statuses else 30
        web_score = scoring.score_website(st.session_state.website_findings) if st.session_state.website_findings else 50
        citations_score = 30  # manual / no verificable en automático todavía

        scores = [
            {"area": "Optimización del Perfil (GBP)", "score": f"{profile_score} / 100", "status": scoring.status_label(profile_score)},
            {"area": "Reseñas y Reputación", "score": f"{review_score} / 100", "status": scoring.status_label(review_score)},
            {"area": "Publicaciones, Fotos y Actividad", "score": f"{photo_score} / 100", "status": scoring.status_label(photo_score)},
            {"area": "Segmentación de Palabras Clave", "score": f"{kw_score} / 100", "status": scoring.status_label(kw_score)},
            {"area": "Sitio Web (SEO Local)", "score": f"{web_score} / 100", "status": scoring.status_label(web_score)},
            {"area": "Citas Locales (Directorios)", "score": f"{citations_score} / 100", "status": scoring.status_label(citations_score)},
        ]
        overall_score = round(sum([profile_score, review_score, photo_score, kw_score, web_score, citations_score]) / 6)

        issues = []
        num = 1
        if place["reviewCount"] < 20:
            issues.append({"num": num, "area": "Volumen de Reseñas", "issue": f"Solo {place['reviewCount']} reseñas en total", "impact": "Baja confianza y débil posicionamiento en el Mapa Local", "severity": "Crítico" if place["reviewCount"] < 10 else "Alto"})
            num += 1
        if place["photoCount"] < 15:
            issues.append({"num": num, "area": "Fotos", "issue": f"Solo {place['photoCount']} fotos en el perfil", "impact": "Menos engagement y solicitudes de \"Cómo llegar\"", "severity": "Alto"})
            num += 1
        if place["website"] in (None, "—"):
            issues.append({"num": num, "area": "Sitio Web", "issue": "El perfil no tiene sitio web enlazado", "impact": "Se pierde tráfico calificado que busca más información", "severity": "Crítico"})
            num += 1
        if place["phone"] in (None, "—"):
            issues.append({"num": num, "area": "Teléfono", "issue": "El perfil no tiene teléfono visible", "impact": "Se pierden llamadas directas desde el perfil", "severity": "Alto"})
            num += 1
        for w in (st.session_state.website_findings or [])[:4]:
            issues.append({"num": num, "area": "Sitio Web", "issue": w["issue"], "impact": w["details"], "severity": w["severity"]})
            num += 1
        if not issues:
            issues.append({"num": 1, "area": "General", "issue": "El perfil cumple con lo básico", "impact": "Aún hay oportunidad de optimización fina", "severity": "Medio"})

        keywords_for_doc = []
        if st.session_state.keyword_rows:
            for r in st.session_state.keyword_rows:
                keywords_for_doc.append({
                    "keyword": r["keyword"], "volume": r.get("volume", "—"),
                    "competition": r.get("competition", "—"), "difficulty": r.get("competition", "—"),
                    "currentUse": r.get("currentUse", "No se usa"),
                })

        data = dict(UNIVERSAL)
        data["auditDate"] = datetime.date.today().strftime("%d de %B de %Y")
        data["preparedBy"] = {"name": prep_name, "title": prep_title, "contact": prep_contact}
        data["business"] = {
            "name": place["name"],
            "shortName": place["name"].split(" — ")[0].split(" - ")[0],
            "website": place["website"],
            "phone": place["phone"],
            "address": place["address"],
            "category": place["category"],
            "categoriesAdd": place["categoriesAdd"],
            "reviews": f"{place['reviewCount']} reseñas | {place['rating']} ★",
            "hours": place["hours"],
            "status": "Reclamado / Verificado",
        }
        data["scores"] = scores
        data["overall"] = {"score": f"{overall_score} / 100", "status": scoring.overall_status_label(overall_score)}
        data["issues"] = issues
        data["keywords"] = keywords_for_doc or [{"keyword": "(agrega palabras clave en el paso 3)", "volume": "—", "competition": "—", "difficulty": "—", "currentUse": "No se usa"}]
        data["reviewRisk"] = [
            f"Actualmente {data['business']['shortName']} tiene {place['reviewCount']} reseñas con {place['rating']}★.",
            "Cada reseña adicional se traduce en más visitas al perfil, más solicitudes de \"Cómo llegar\" y más llamadas.",
            "Mientras el perfil se mantenga con pocas reseñas, Google seguirá prefiriendo mostrar a la competencia en el Mapa Local.",
        ]
        data["websiteNote"] = f"Revisión técnica en vivo de {place['website']}." if place["website"] not in (None, "—") else "No se auditó un sitio web (no está enlazado en el perfil)."
        data["websiteIssues"] = st.session_state.website_findings or [{"num": 1, "issue": "Sin sitio web enlazado", "details": "El perfil de Google no tiene un sitio web para auditar.", "severity": "Crítico"}]
        data["competitors"] = st.session_state.competitors or [{"name": "(agrega el término de búsqueda en el paso 2)", "reviewCount": "—", "rating": "—", "website": "—"}]
        avg_comp_reviews = None
        try:
            counts = [c["reviewCount"] for c in st.session_state.competitors if isinstance(c.get("reviewCount"), (int, float))]
            avg_comp_reviews = round(sum(counts) / len(counts)) if counts else None
        except Exception:
            avg_comp_reviews = None
        data["growthTargets"] = [
            {"kpi": "Reseñas en Google", "current": str(place["reviewCount"]), "target": f"{max(avg_comp_reviews or 30, place['reviewCount'] + 20)}+"},
            {"kpi": "Calificación Promedio", "current": str(place["rating"]), "target": "4.7+"},
            {"kpi": "Publicaciones GBP / mes", "current": "0", "target": "8"},
            {"kpi": "Fotos en el Perfil", "current": str(place["photoCount"]), "target": "30+"},
            {"kpi": "Citas / Directorios Activos", "current": "Por confirmar", "target": "13+"},
        ]
        data["citations"] = citations_default
        data["actionPlan"] = [
            {"phase": "Semana 1", "task": "Responder TODAS las reseñas con respuestas cordiales y con palabras clave", "owner": prep_name, "priority": "Crítico"},
            {"phase": "Semana 1", "task": "Activar automatización de solicitud de reseñas en GoHighLevel", "owner": prep_name, "priority": "Crítico"},
            {"phase": "Semana 2", "task": "Corregir categoría, atributos y formato de dirección en GBP", "owner": prep_name, "priority": "Alto"},
            {"phase": "Mes 1", "task": "Reescribir descripción, subir fotos, configurar servicios con descripciones y precios", "owner": prep_name, "priority": "Alto"},
            {"phase": "Mes 1", "task": "Publicar 2 posts de GBP por semana", "owner": prep_name, "priority": "Alto"},
            {"phase": "Mes 1–2", "task": "Reclamar y unificar NAP en los directorios listados", "owner": prep_name, "priority": "Alto"},
            {"phase": "Mes 2–3", "task": "Optimizar el sitio web: títulos, H1, schema, velocidad", "owner": "Equipo Web", "priority": "Medio"},
            {"phase": "Mensual", "task": "Seguimiento de posiciones, llamadas, direcciones y clics; reporte mensual", "owner": prep_name, "priority": "Medio"},
        ]
        data["packages"] = packages

        buf = io.BytesIO()
        tmp_path = "/tmp/_reporte_generado.docx"
        build_report(data, tmp_path)
        with open(tmp_path, "rb") as f:
            buf.write(f.read())
        buf.seek(0)

        st.success("¡Reporte generado!")
        st.download_button(
            "⬇️ Descargar reporte Word",
            data=buf,
            file_name=f"Auditoria_{data['business']['shortName'].replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
