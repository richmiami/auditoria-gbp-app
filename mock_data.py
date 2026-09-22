"""Datos de ejemplo para probar report_generator.py sin llamar APIs reales."""

from universal_content import UNIVERSAL, DEFAULT_PREPARED_BY


def mock_data():
    d = dict(UNIVERSAL)
    d["auditDate"] = "21 de septiembre de 2026"
    d["preparedBy"] = DEFAULT_PREPARED_BY
    d["business"] = {
        "name": "Climas del Valle — Aire Acondicionado y Refrigeración",
        "shortName": "Climas del Valle",
        "website": "climasdelvalle.mx",
        "phone": "+52 33 1234 5678",
        "address": "Av. Patria 1450, Jardines de Guadalupe, Zapopan, Jalisco 45030",
        "category": "Servicio de aire acondicionado",
        "categoriesAdd": "Empresa de refrigeración, Instalación de aire acondicionado",
        "reviews": "9 reseñas | 4.1 ★",
        "hours": "Lun–Sáb 8:00 AM–7:00 PM",
        "status": "Reclamado / Verificado",
    }
    d["scores"] = [
        {"area": "Optimización del Perfil (GBP)", "score": "48 / 100", "status": "Necesita Trabajo"},
        {"area": "Reseñas y Reputación", "score": "28 / 100", "status": "Débil"},
        {"area": "Publicaciones, Fotos y Actividad", "score": "22 / 100", "status": "Débil"},
        {"area": "Segmentación de Palabras Clave", "score": "33 / 100", "status": "Débil"},
        {"area": "Sitio Web (SEO Local)", "score": "18 / 100", "status": "Crítico"},
        {"area": "Citas Locales (Directorios)", "score": "30 / 100", "status": "Débil"},
    ]
    d["overall"] = {"score": "30 / 100", "status": "Deficiente"}
    d["issues"] = [
        {"num": 1, "area": "Volumen de Reseñas", "issue": "Solo 9 reseñas en total", "impact": "Baja confianza", "severity": "Crítico"},
        {"num": 2, "area": "Respuesta a Reseñas", "issue": "Última reseña sin respuesta", "impact": "Señala inactividad", "severity": "Alto"},
        {"num": 3, "area": "Fotos", "issue": "Sin fotos recientes", "impact": "Bajo engagement", "severity": "Alto"},
    ]
    d["keywords"] = [
        {"keyword": "aire acondicionado Zapopan", "volume": "880/mes", "competition": "Alta", "difficulty": "Alta", "currentUse": "No se usa"},
        {"keyword": "reparación de aire acondicionado Guadalajara", "volume": "1,300/mes", "competition": "Alta", "difficulty": "Alta", "currentUse": "No se usa"},
        {"keyword": "recarga de gas refrigerante Guadalajara", "volume": "210/mes", "competition": "Media", "difficulty": "Media", "currentUse": "Parcial"},
    ]
    d["reviewRisk"] = [
        "Actualmente Climas del Valle tiene 9 reseñas con 4.1★.",
        "Cada reseña adicional se traduce en más visitas y más llamadas.",
        "Mientras el perfil tenga pocas reseñas, Google preferirá mostrar a la competencia.",
    ]
    d["websiteNote"] = "Revisión en vivo de climasdelvalle.mx."
    d["websiteIssues"] = [
        {"num": 1, "issue": "Sin metadescripción", "details": "No se encontró <meta name=description> en la portada", "severity": "Alto"},
        {"num": 2, "issue": "Sin datos estructurados", "details": "No hay JSON-LD de tipo LocalBusiness", "severity": "Alto"},
    ]
    d["competitors"] = [
        {"name": "Refrigeración Jalisco", "reviewCount": 45, "rating": 4.6, "website": "refrigeracionjalisco.mx"},
        {"name": "Clima Total GDL", "reviewCount": 30, "rating": 4.4, "website": "climatotalgdl.com"},
    ]
    d["growthTargets"] = [
        {"kpi": "Reseñas en Google", "current": "9", "target": "45+"},
        {"kpi": "Calificación Promedio", "current": "4.1", "target": "4.7+"},
    ]
    d["citations"] = [
        {"platform": "Apple Maps", "type": "Mapa", "status": "No reclamado", "action": "Reclamar y agregar NAP", "priority": "Crítico"},
        {"platform": "Facebook", "type": "Social", "status": "Inactivo", "action": "Reactivar y vincular", "priority": "Alto"},
    ]
    d["actionPlan"] = [
        {"phase": "Semana 1", "task": "Responder todas las reseñas", "owner": "Ricardo Arreguín", "priority": "Crítico"},
        {"phase": "Mes 1", "task": "Optimizar perfil completo", "owner": "Ricardo Arreguín", "priority": "Alto"},
    ]
    return d
