# Auditoría GBP / SEO Local — App con datos reales

App en Python (Streamlit) que reemplaza el llenado manual de la plantilla de Word:
buscas el negocio, trae datos reales de Google Maps y volumen de búsquedas reales,
audita el sitio web en vivo, y te da un `.docx` con el mismo diseño de marca, listo
para enviar al prospecto.

## Qué es automático y qué no

| Sección del reporte | Fuente | ¿En vivo? |
|---|---|---|
| Datos del negocio, reseñas, calificación, fotos, categoría | Google Places API (New) | ✅ Sí |
| Competidores en el Mapa Local | Google Places API (New) | ✅ Sí |
| Volumen de búsqueda de palabras clave | Keywords Everywhere | ✅ Sí |
| Hallazgos técnicos del sitio web (título, meta, H1, schema, HTTPS) | Auditor propio (sin API de pago) | ✅ Sí |
| Estadísticas de reseñas / GoHighLevel / GBP (las de "por qué importa") | Investigación de industria (BrightLocal, etc.) | Fijas, con fuente citada — no cambian por negocio |
| Citas en directorios (Apple Maps, Waze, Facebook, etc.) | — | ❌ Checklist manual editable (verificar cada uno cuesta una API extra por plataforma) |
| Plan de acción de 90 días, paquetes de precio | — | Plantilla editable, precargada con valores razonables |

## 1. Consigue tus dos API keys

### Google Places API (New) — datos de Maps/GBP

1. Entra a **console.cloud.google.com** y crea un proyecto (o usa uno existente).
2. Activa la facturación: te van a pedir una tarjeta, pero **Google te regala $200 USD de crédito cada mes**, automáticamente — no es un pago que hagas tú. Con el volumen de auditorías que vas a hacer (unas cuantas por semana), es prácticamente imposible que te pases de ese crédito.
3. En el buscador de la consola, activa **"Places API (New)"**.
4. Ve a **APIs y servicios → Credenciales → Crear credenciales → Clave de API**.
5. Copia esa clave — la vas a pegar en `secrets.toml` (ver paso 3 más abajo).
6. (Opcional pero recomendado) Restringe la key para que solo funcione con "Places API (New)", así aunque alguien la vea no puede usarla para otra cosa.

### Keywords Everywhere — volumen de búsqueda

1. Entra a **keywordseverywhere.com** y crea una cuenta.
2. Compra un paquete de créditos (desde ~$10 USD, alcanza para miles de consultas).
3. En tu cuenta, ve a **API Access** y copia tu API key.

## 2. Corre la app en tu computadora (para probarla hoy mismo)

Necesitas tener [Python](https://www.python.org/downloads/) instalado (3.10 o más nuevo).

```bash
# 1. Entra a la carpeta de la app
cd webapp

# 2. Instala las librerías necesarias
pip install -r requirements.txt

# 3. Copia el archivo de ejemplo de secrets y pon tus keys reales
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# ábrelo con el Bloc de notas / TextEdit y reemplaza los valores de ejemplo

# 4. Corre la app
streamlit run app.py
```

Se va a abrir sola en tu navegador (normalmente `http://localhost:8501`). Mientras
corra en tu compu, tus keys están seguras — nunca salen de tu máquina.

## 3. (Opcional) Ponerla en internet gratis con un link — Streamlit Community Cloud

Así la puedes abrir desde tu celular o compartirle el link a alguien de tu equipo,
sin pagar hosting.

1. Crea una cuenta gratis en **github.com** (si no tienes) y sube esta carpeta `webapp/`
   como un repositorio nuevo (puedes arrastrar los archivos desde la web de GitHub,
   no hace falta usar la terminal).
   - **Importante:** NO subas tu archivo `.streamlit/secrets.toml` real a GitHub — solo
     sube el `.example`. GitHub es público a menos que marques el repo como privado.
2. Entra a **share.streamlit.io** con tu cuenta de GitHub.
3. Clic en **"New app"**, elige tu repositorio y el archivo `app.py`.
4. Antes de darle "Deploy", abre **"Advanced settings" → "Secrets"** y pega ahí el
   contenido de tu `secrets.toml` real (con tus keys de verdad). Esto las guarda
   cifradas en el servidor de Streamlit, nunca visibles en el código.
5. Dale **Deploy**. En un par de minutos tienes un link tipo
   `https://tu-app.streamlit.app` que puedes abrir desde cualquier dispositivo.

## 4. Cómo usarla

1. **Paso 1:** escribe el nombre del negocio + ciudad tal como lo buscarías en Google
   Maps → clic en "Buscar en Google Maps" → revisa/ajusta los datos que trajo.
2. **Paso 2:** escribe el término de búsqueda del nicho (ej. "aire acondicionado en
   Zapopan") → clic en "Buscar competidores reales".
3. **Paso 3:** pega tus palabras clave (una por línea) → clic en "Obtener volumen de
   búsqueda real".
4. **Paso 4:** clic en "Auditar sitio web" (usa el sitio que trajo el paso 1).
5. **Paso 5:** ajusta precios de los paquetes si quieres.
6. **Paso 6:** clic en "Generar reporte Word" → descarga el `.docx` listo para enviar.

## 5. Ajustar el contenido de venta (estadísticas, precios, textos)

Todo lo que **no** cambia por negocio (estadísticas de reseñas, explicación de
GoHighLevel, paquetes de precio por defecto, próximos pasos) vive en
**`universal_content.py`**. Ábrelo y edita el texto o los números libremente — no
necesitas tocar el resto del código.

Las fórmulas de puntuación (cómo se calculan los `__/100` de cada área) están en
**`scoring.py`**, con comentarios explicando cada una — son un punto de partida
razonable, no un estándar fijo. Puedes ajustarlas ahí mismo.

## 6. Estructura de archivos

```
webapp/
├── app.py                 # La interfaz (Streamlit) — el "formulario"
├── integrations.py        # Llamadas reales a Google Places, Keywords Everywhere, auditor de sitio web
├── scoring.py             # Fórmulas de puntuación 0-100 por área
├── report_generator.py    # Arma el .docx con el diseño de marca (python-docx)
├── universal_content.py   # Estadísticas, pitch de GoHighLevel, paquetes de precio (edítalo aquí)
├── mock_data.py           # Datos de prueba (para probar report_generator sin llamar APIs)
├── requirements.txt
└── .streamlit/
    └── secrets.toml.example
```

## Límites a tener en cuenta

- El auditor de sitio web es una revisión técnica básica (título, meta descripción,
  H1, datos estructurados, HTTPS, cuánto texto ve un rastreador). No reemplaza una
  auditoría SEO completa, pero sí detecta los problemas más comunes y graves.
- El "¿ya se usa esta palabra clave?" es una coincidencia de texto contra el nombre
  y categoría del negocio en Google — no es un rastreador de posiciones (rank
  tracker) real. Para eso se necesitaría otra API adicional (ej. DataForSEO SERP API).
- Las citas en directorios (Apple Maps, Waze, redes sociales, etc.) se entregan como
  checklist manual: verificarlas todas automáticamente requeriría contratar una API
  extra por cada plataforma, lo cual no vale la pena para el volumen que vas a manejar.
