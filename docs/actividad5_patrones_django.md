# Actividad 5 — Patrones de diseño en Django

## 1. Objetivo
Aplicar **dos** patrones en capas distintas del proyecto:
1) **Controladores**: Vistas basadas en clases (**CBV**) + **mixins**.
2) **Modelos**: **Signals** + **normalización** de datos para mantener `avg_rating` y `reviews_count`.

---

## 2. Patrones aplicados

### 2.1 CBV + mixins (Controladores)
**Archivos:**
- `places/views_cbv.py`
- `places/forms.py`
- `places/urls.py`
- `routecraft/urls.py`

**Qué se hizo:**
- Migración de vistas CRUD de `Place` y creación de reseñas a **Class-Based Views**.
- Uso de **`LoginRequiredMixin`** para proteger creación/edición/eliminación.

**Beneficios:**
- Menos **boilerplate** que las FBV.
- Reutilización de **mixins** (autenticación, permisos, paginación).
- Plantillas convencionales (`place_form.html`, `place_confirm_delete.html`).

**Evidencia:**
- Nuevas rutas: `/places/`, `/places/<id>/`, `/places/create/`, etc.
- Formularios conectados a `PlaceForm` y `ReviewForm`.

---

### 2.2 Signals + normalización (Modelos)
**Archivos:**
- `places/models.py` (campos nuevos: `avg_rating`, `reviews_count`, `get_absolute_url`)
- `places/signals.py`
- `places/apps.py` (registro de señales)
- `routecraft/settings.py` (`'places.apps.PlacesConfig'` en `INSTALLED_APPS`)

**Qué se hizo:**
- Se agregaron campos normalizados (`avg_rating`, `reviews_count`) al modelo `Place`.
- Señales **`post_save`** y **`post_delete`** sobre `Review` recalculan automáticamente ambos campos.

**Beneficios:**
- **Consistencia**: no dependemos de calcular promedios cada vez.
- Menor carga en vistas; los valores quedan materializados.
- Fácil auditoría y caché de consultas.

**Evidencia:**
- Tras crear/borrar una `Review` los campos del `Place` cambian al instante.

---

## 3. Decisiones de diseño

- **CBV** en lugar de FBV: mejor composición, menos duplicación.
- **LoginRequiredMixin**: asegura operaciones CRUD para usuarios autenticados.
- **Signals**: desacoplan la lógica de agregación del flujo de las vistas.
- **Normalización**: almacenamos agregados para listar más rápido.

**Alternativas evaluadas:**  
- Calcular promedio “al vuelo”: simple, pero costoso y repetitivo.  
- Jobs periódicos: innecesario y con latencia para datos en tiempo real.

---

## 4. Cómo probar

1. **CBV**
   - Ir a `/places/` → lista paginada.
   - Crear un lugar en `/places/create/` (si estás logueado).
   - Editar/eliminar desde la vista de detalle.

2. **Signals**
   - Crear una `Review` (desde admin o `/reviews/create/` si expuesto).
   - Verifica en Admin o en detalle del `Place` que `avg_rating` y `reviews_count` se actualizan.
   - Borrar la `Review` y comprobar los nuevos valores.

---

## 5. Impacto y métricas

- **Tiempo de respuesta de listados** ↓ al usar datos normalizados.
- **Mantenibilidad** ↑ (CBV + mixins) y menor acoplamiento.
- **Riesgos:** señales mal registradas → no actualizarían agregados.
- **Mitigaciones:** pruebas manuales; revisar `apps.py → ready()` y `INSTALLED_APPS`.

---

## 6. Rastro de cambios

- `places/forms.py` → formularios `PlaceForm` y `ReviewForm`.
- `places/views_cbv.py` → CBV CRUD + mixins.
- `places/urls.py` y `routecraft/urls.py` → rutas.
- `places/models.py` → `avg_rating`, `reviews_count`, `get_absolute_url`.
- `places/signals.py` → recálculo tras `post_save` / `post_delete`.
- Migraciones aplicadas para nuevos campos.

---
