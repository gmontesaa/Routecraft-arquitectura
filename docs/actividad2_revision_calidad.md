# Actividad 2 — Revisión autocrítica de calidad

## 1. Usabilidad
- **Qué cumple hoy:** navegación por ciudades, reseñas básicas, plantillas con estructura clara.
- **Hallazgos (pruebas rápidas):** [describe 3–5 tareas y si fueron fáciles/difíciles].
- **A mejorar:** búsqueda tolerante a errores (typos), paginación en listados, feedback de “cargando”.
- **Acciones & métricas:** tasa de éxito de tarea ≥90%, tiempo mediano < 15s, NPS > 30.

## 2. Compatibilidad
- **Qué cumple hoy:** Django estable, funciona en Chrome/Edge.
- **Riesgos:** dependencias sin pin exacto, pruebas móviles faltantes.
- **Acciones:** fijar versiones (pip-compile), pruebas en Android/iOS con Lighthouse.

## 3. Rendimiento
- **Qué cumple hoy:** consultas ORM simples.
- **Cuellos de botella:** llamadas externas sin caché (rutas), distancia calculada en caliente.
- **Acciones:** caché 15 min para rutas, `select_related/prefetch`, compresión estáticos.
- **Métricas:** TTFB < 500ms (páginas sin API externa), p95 < 1.5s.

## 4. Seguridad
- **Qué cumple hoy:** `.env` para claves, CSRF por defecto.
- **Riesgos:** `@csrf_exempt` innecesarios, `requests` sin `timeout`, logs verbosos.
- **Acciones:** quitar `csrf_exempt` salvo webhooks, `timeout=10`, rotar API keys, validar inputs.

## 5. Plan de inversión
- **Opción A (ahorro):** OSRM self-hosted para ruteo (costo infra, 0 variable).
- **Opción B (premium):** Google Routes Advanced (↓latencia, ↑confiabilidad).
- **Decisión:** [elige], costo estimado, impacto en métricas, plan de monitoreo.
