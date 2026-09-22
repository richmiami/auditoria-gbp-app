"""
Contenido universal reutilizable en TODOS los reportes: estadísticas de la industria
(con fuente citada), la explicación del servicio de GoHighLevel, los paquetes de
inversión y los próximos pasos. Esto es lo que NO cambia por prospecto — lo que sí
cambia (negocio, competidores, palabras clave) se llena con datos en vivo en app.py.

Edita este archivo para ajustar precios, estadísticas o el texto de venta sin tocar
el resto del código.
"""

DEFAULT_PREPARED_BY = {
    "name": "Ricardo Arreguín",
    "title": "Especialista en Reputación Digital y Marketing Local · GoHighLevel Partner",
    "contact": "ricardo.arreguin0@gmail.com · [Tu teléfono / WhatsApp]",
}

# Contenido "universal" reutilizable en cada reporte (estadísticas con fuente citada).
UNIVERSAL = {
    "reviewsIntro": (
        "Antes de invertir en publicidad o en un sitio web nuevo, la reputación en Google es el filtro "
        "por el que pasa prácticamente todo cliente potencial. Los siguientes datos, de estudios "
        "independientes de la industria, muestran por qué las reseñas son hoy el factor de decisión "
        "número uno en la búsqueda local."
    ),
    "reviewStats": [
        {"number": "93%", "label": "de los consumidores lee reseñas antes de visitar un negocio local", "source": "BrightLocal, Local Consumer Review Survey"},
        {"number": "47%", "label": "no considerará un negocio con menos de 20 reseñas", "source": "BrightLocal, 2026"},
        {"number": "31%", "label": "solo elegirá negocios con 4.5+ estrellas — casi el doble que hace un año", "source": "BrightLocal, 2026"},
        {"number": "74%", "label": "revisa al menos 2 plataformas de reseñas antes de decidir", "source": "BrightLocal / SurfSigma"},
    ],
    "ghl": {
        "intro": (
            "La causa raíz casi nunca es que los clientes estén insatisfechos — es que nadie les pide la "
            "reseña en el momento correcto, de forma consistente. GoHighLevel automatiza ese proceso por "
            "completo, convirtiendo cada cliente satisfecho en una reseña pública."
        ),
        "steps": [
            "Disparador automático: al marcar un servicio como \"completado\", el sistema envía una solicitud personalizada por SMS y/o correo.",
            "Enrutamiento inteligente: clientes satisfechos van directo a Google; insatisfechos a un formulario privado.",
            "Seguimiento automático: hasta 3 recordatorios si no hay respuesta — típicamente duplica el volumen de reseñas.",
            "Respuestas con IA a cada nueva reseña, o alerta para responder personalmente.",
            "Panel centralizado y reporte mensual de calificación, reseñas nuevas y tasa de conversión.",
        ],
        "stats": [
            {"number": "200–500%", "label": "incremento en volumen de reseñas en 3–6 meses al automatizar", "source": "GoHighLevel, Reputation Management"},
            {"number": "28%", "label": "más conversión de visitantes gracias al widget de reseñas", "source": "Casos de estudio GoHighLevel"},
            {"number": "10–25%", "label": "de las solicitudes automatizadas se convierte en reseña publicada", "source": "Benchmarks GoHighLevel"},
            {"number": "6 hrs/sem", "label": "que el equipo recupera al eliminar el seguimiento manual", "source": "Caso de estudio de implementación"},
        ],
        "caseStudy": [
            "En una implementación documentada, un negocio local pasó de 3.4 a 4.9 estrellas y sumó 100+ reseñas de 5 estrellas en 12 meses.",
            "Ese mismo negocio reportó un incremento del 30% en ingresos en el mismo periodo.",
            "Otro caso: una empresa de servicio a domicilio pasó de 12 a 71 reseñas en 6 semanas, subiendo del puesto #6 al #2 en el Mapa Local.",
            "Fuente: Casos de estudio de implementación de Reputation Manager, GoHighLevel.",
        ],
    },
    "gbpOpt": {
        "intro": "Un perfil de Google completo es el activo digital con mayor retorno inmediato para un negocio local.",
        "stats": [
            {"number": "2.7x", "label": "más probabilidad de ser percibido como confiable con perfil completo", "source": "Datos de Google"},
            {"number": "7x", "label": "más clics en resultados de búsqueda para perfiles optimizados", "source": "SearchEndurance, GBP Statistics"},
            {"number": "35%", "label": "más clics al sitio web en perfiles con fotos actualizadas", "source": "Google Business Profile data"},
            {"number": "+42%", "label": "más solicitudes de \"Cómo llegar\" con fotos frecuentes", "source": "SearchEndurance, GBP Statistics"},
        ],
        "actions": [
            "Optimizar categoría principal y secundarias según servicios de mayor búsqueda.",
            "Reescribir la descripción integrando palabras clave y zonas donde opera el negocio.",
            "Configurar servicios y productos con descripciones completas y precios de referencia.",
            "Subir mínimo 15–20 fotos reales y renovarlas cada 60–90 días.",
            "Sembrar preguntas y respuestas con las dudas más comunes.",
            "Activar WhatsApp/mensajería y enlace de agendamiento con seguimiento UTM.",
            "Publicar actualizaciones semanales con ofertas y proyectos.",
            "Corregir inconsistencias de NAP entre el perfil y los directorios.",
        ],
    },
    "pricingIntro": "Estos son los paquetes estándar. Se ajustan según volumen de servicios y objetivos del negocio.",
    "packages": [
        {"name": "Reputación Esencial", "price": "$3,900 MXN/mes", "includes": [
            "Automatización de solicitudes de reseñas (GoHighLevel)",
            "Respuestas asistidas por IA a reseñas nuevas",
            "Alertas de reseñas negativas en tiempo real",
            "Reporte mensual de reseñas y calificación",
        ]},
        {"name": "Crecimiento Local", "price": "$6,900 MXN/mes", "highlight": True, "includes": [
            "Todo lo de Reputación Esencial",
            "Optimización completa del perfil de Google",
            "2 publicaciones GBP por semana",
            "Gestión de 13+ citas/directorios con NAP consistente",
            "Dashboard de KPIs y reporte mensual",
        ]},
        {"name": "Dominio de Mercado", "price": "$11,900 MXN/mes", "includes": [
            "Todo lo de Crecimiento Local",
            "Auditoría y optimización técnica del sitio web",
            "4 artículos de blog al mes",
            "Seguimiento de posicionamiento por zona (geo-grid)",
            "Soporte prioritario",
        ]},
    ],
    "roiPoints": [
        "Un solo cliente nuevo generado por el perfil optimizado normalmente cubre el costo del paquete mensual.",
        "Pasar de solicitudes manuales a automatizadas genera 200–500% más reseñas en 3–6 meses.",
        "Un perfil completo y optimizado genera hasta 7x más clics que uno incompleto.",
        "El servicio se factura mes a mes, con resultados y reportes medibles y transparentes.",
    ],
    "nextStepsIntro": "Este diagnóstico es el punto de partida. El siguiente paso es platicarlo juntos y definir el plan de implementación.",
    "nextSteps": [
        "Agendar una llamada de 20 minutos para revisar este diagnóstico y resolver dudas.",
        "Elegir el paquete que mejor se ajuste a los objetivos y presupuesto del negocio.",
        "Firmar el acuerdo de servicio y realizar el primer pago para iniciar la configuración.",
        "Comenzar la implementación: automatización activa en la primera semana; GBP optimizado en dos.",
    ],
}

